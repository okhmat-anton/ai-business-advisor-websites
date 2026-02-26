"""
Server public IP detection with caching.
Used for DNS verification and domain settings UI.
"""

import time
import logging
import httpx

from app.core import settings

logger = logging.getLogger(__name__)

# Cache: (ip_string, timestamp)
_cached_ip: str = ""
_cached_at: float = 0
_CACHE_TTL = 3600  # 1 hour


async def get_server_ip() -> str:
    """Get server public IP. Uses SERVER_IP from settings, or auto-detects with caching."""
    if settings.SERVER_IP:
        return settings.SERVER_IP

    global _cached_ip, _cached_at
    now = time.time()
    if _cached_ip and (now - _cached_at) < _CACHE_TTL:
        return _cached_ip

    ip = await _detect_public_ip()
    if ip:
        _cached_ip = ip
        _cached_at = now
        logger.info(f"Auto-detected server public IP: {ip}")
    return ip


async def _detect_public_ip() -> str:
    """Auto-detect public IP via external services."""
    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
    ]
    for url in services:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.text.strip()
        except Exception:
            continue
    return ""
