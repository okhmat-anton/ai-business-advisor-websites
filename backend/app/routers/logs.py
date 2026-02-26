"""
Logs API router - view server/container logs for debugging.
Supports JWT auth, local Agent API key, and parent project agent key validation.
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from pydantic import BaseModel

from app.core.auth import get_current_user, CurrentUser
from app.core import settings

router = APIRouter(prefix="/logs", tags=["logs"])

logger = logging.getLogger("uvicorn.error")

# Container names used in docker-compose
ALLOWED_SERVICES = {"api", "worker", "postgres", "mongodb", "redis", "nginx", "frontend"}

# Agent API key from settings (set AGENT_API_KEY in .env)
AGENT_API_KEY = settings.AGENT_API_KEY


async def _validate_agent_key_via_parent(agent_key: str) -> bool:
    """Validate agent key by calling parent project context endpoint."""
    project_id = settings.AGENT_PROJECT_ID
    if not project_id:
        return False
    url = f"{settings.EXTERNAL_AUTH_URL}/api/v1/agent/{project_id}/context"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url, headers={"X-Agent-Key": agent_key})
            return resp.status_code == 200
    except Exception:
        return False


async def verify_logs_access(
    request: Request,
    x_agent_key: Optional[str] = Header(None),
):
    """
    Allow access via:
    1. Local AGENT_API_KEY match (X-Agent-Key header or Bearer)
    2. Parent project agent key validation via app.akm-advisor.com
    3. JWT Bearer token
    """
    # Check local agent key first
    if x_agent_key and AGENT_API_KEY and x_agent_key == AGENT_API_KEY:
        return

    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer ") and AGENT_API_KEY and auth_header[7:] == AGENT_API_KEY:
        return

    # Validate agent key via parent project API
    key_to_check = x_agent_key or (auth_header[7:] if auth_header.startswith("Bearer ") else None)
    if key_to_check and key_to_check.startswith("agent_"):
        if await _validate_agent_key_via_parent(key_to_check):
            return

    # Fallback to standard JWT auth
    try:
        from fastapi.security import HTTPAuthorizationCredentials
        token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
        if not token:
            raise HTTPException(status_code=401, detail="Missing authentication")
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        await get_current_user(creds)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication. Use JWT Bearer token or X-Agent-Key header.",
        )


class LogEntry(BaseModel):
    """Single log response."""
    service: str
    lines: list[str]
    total_lines: int
    tail: int
    timestamp: str


class LogsListResponse(BaseModel):
    """Available services list."""
    services: list[str]
    note: str


@router.get("", response_model=LogsListResponse)
async def list_log_services(
    _auth=Depends(verify_logs_access),
):
    """List available services whose logs can be viewed."""
    return LogsListResponse(
        services=sorted(ALLOWED_SERVICES),
        note="Use GET /api/v1/logs/{service} to view logs for a specific service. "
             "Use GET /api/v1/logs/app for application-level Python logs.",
    )


@router.get("/app", response_model=LogEntry)
async def get_app_logs(
    tail: int = Query(100, ge=1, le=5000, description="Number of last lines to return"),
    search: Optional[str] = Query(None, description="Filter lines containing this text (case-insensitive)"),
    level: Optional[str] = Query(None, description="Filter by log level: ERROR, WARNING, INFO, DEBUG"),
    _auth=Depends(verify_logs_access),
):
    """
    Get application-level Python/uvicorn logs from the API container.
    Reads from /tmp/app.log if file logging is configured,
    otherwise falls back to Docker logs for 'api' service.
    """
    # Try file-based log first
    log_file = os.environ.get("APP_LOG_FILE", "/tmp/app.log")
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                all_lines = f.readlines()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cannot read log file: {e}")
    else:
        # Fallback to docker logs for api container
        all_lines = await _docker_logs("sb-api", tail=tail * 2)

    # Apply filters
    lines = _filter_lines(all_lines, search=search, level=level)

    # Tail
    lines = lines[-tail:]

    return LogEntry(
        service="app",
        lines=[line.rstrip("\n") for line in lines],
        total_lines=len(lines),
        tail=tail,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get("/{service}", response_model=LogEntry)
async def get_service_logs(
    service: str,
    tail: int = Query(100, ge=1, le=5000, description="Number of last lines to return"),
    search: Optional[str] = Query(None, description="Filter lines containing this text (case-insensitive)"),
    since: Optional[str] = Query(None, description="Show logs since (e.g. '1h', '30m', '2h30m')"),
    _auth=Depends(verify_logs_access),
):
    """
    Get Docker container logs for a specific service.
    Services: api, worker, postgres, mongodb, redis, nginx, frontend.
    """
    if service not in ALLOWED_SERVICES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown service '{service}'. Allowed: {sorted(ALLOWED_SERVICES)}",
        )

    container_name = f"sb-{service}"
    lines = await _docker_logs(container_name, tail=tail * 2 if search else tail, since=since)

    # Apply search filter
    if search:
        search_lower = search.lower()
        lines = [l for l in lines if search_lower in l.lower()]
        lines = lines[-tail:]

    return LogEntry(
        service=service,
        lines=[line.rstrip("\n") for line in lines],
        total_lines=len(lines),
        tail=tail,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


async def _docker_logs(
    container_name: str,
    tail: int = 100,
    since: Optional[str] = None,
) -> list[str]:
    """Execute docker logs command and return lines."""
    cmd = ["docker", "logs", "--tail", str(tail)]

    if since:
        cmd.extend(["--since", since])

    cmd.append(container_name)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)

        # Docker logs outputs to both stdout and stderr
        output = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")
        lines = output.splitlines()
        return lines

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout reading container logs")
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Docker CLI not available inside container. "
                   "Mount docker.sock to enable log access.",
        )
    except Exception as e:
        logger.error(f"Failed to read docker logs for {container_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {e}")


def _filter_lines(
    lines: list[str],
    search: Optional[str] = None,
    level: Optional[str] = None,
) -> list[str]:
    """Filter log lines by search text and/or log level."""
    result = lines

    if level:
        level_upper = level.upper()
        result = [l for l in result if level_upper in l.upper()]

    if search:
        search_lower = search.lower()
        result = [l for l in result if search_lower in l.lower()]

    return result
