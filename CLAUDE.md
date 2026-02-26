# CLAUDE.md

## Project Overview

Tilda-like site builder — модуль конструктора сайтов, интегрируемый в основной проект app.akm-advisor.com. Авторизация приходит извне через JWT. Фронтенд работает с моковыми данными или реальным бекендом (переключение через `VITE_USE_MOCK`).

## Tech Stack

- **Frontend:** Vue 3 (Composition API, `<script setup>`) + TypeScript + Vuetify 3
- **Backend:** FastAPI + SQLAlchemy (async) + Motor (MongoDB) + Celery
- **Databases:** PostgreSQL (sites, pages, domains), MongoDB (block content), Redis (cache + Celery broker)
- **State:** Pinia
- **Routing:** Vue Router 4
- **HTTP:** Axios (instance in `src/api/index.ts`, switcher in `src/api/api.ts`)
- **Build:** Vite 7, vite-plugin-vuetify
- **Icons:** @mdi/font (Material Design Icons)
- **Drag & Drop:** vuedraggable
- **Styles:** SCSS (scoped + global in `src/styles/`)
- **Deploy:** Docker + docker-compose + Nginx

## Project Structure

```
frontend/               # Vue 3 SPA
  src/
    api/                # Axios instance + mock/real API + switcher
    components/
      blocks/           # 20 block components (cover, about, text, etc.)
      editor/           # Editor UI (canvas, toolbar, panels, modals)
      site/             # Site/page management dialogs
      common/           # Shared UI (header, color picker, dialogs)
    composables/        # useAuth, useUndoRedo, useAutoSave, useResponsive
    layouts/            # EditorLayout, PublicLayout
    pages/              # Dashboard, Editor, Preview, Public pages
    router/             # Vue Router config
    stores/             # Pinia stores (auth, editor, site, ui)
    styles/             # SCSS: main, editor, blocks
    types/              # TypeScript interfaces (block, site, editor, api)
    utils/              # helpers, blockRegistry

backend/                # FastAPI backend
  app/
    core/               # Settings, database, mongodb, redis, auth
    models/             # SQLAlchemy models (Site, Page, Domain)
    schemas/            # Pydantic request/response schemas
    routers/            # API endpoints (sites, pages, blocks, uploads)
    tasks/              # Celery tasks (publish)
    data/               # Block template library data
    main.py             # FastAPI app entry point
    celery_app.py       # Celery configuration
  alembic/              # Database migrations
  requirements.txt
  Dockerfile

nginx/                  # Nginx reverse proxy config
docker-compose.yml      # Development stack
docker-compose.prod.yml # Production overrides
deploy.sh               # Self-deployment script
```

## Commands

```bash
# Frontend
make install            # npm install
make dev                # Dev server on port 10669
make build              # Production build (vue-tsc + vite build)
make lint               # TypeScript type-check
make update             # git pull + install + build + dev
make clean              # Remove dist and cache

# Backend
make backend-install    # pip install -r requirements.txt
make backend-dev        # FastAPI dev server on port 8000
make migrate            # Run alembic migrations
make migrate-create MSG="desc"  # Create new migration

# Docker
make docker-up          # Start all services (dev mode)
make docker-down        # Stop all services
make docker-build       # Build images
make docker-logs        # View logs (SVC=api for specific)
make docker-status      # Service status
make docker-clean       # Remove everything + data

# Deploy
make deploy             # Deploy dev environment
make deploy-prod        # Deploy production
make help               # List all commands
```

## Key Conventions

- All Vue components use Composition API with `<script setup lang="ts">`
- Comments in code in English
- Imports use `@/` alias (resolves to `src/`)
- Block components receive `content` and `settings` props
- Block types are mapped to components via `src/utils/blockRegistry.ts` (lazy async imports)
- API switcher in `src/api/api.ts` — uses mock or real backend based on `VITE_USE_MOCK`
- Stores: `editorStore` (blocks, undo/redo), `siteStore` (sites, pages), `uiStore` (panels, device preview), `authStore` (JWT)

## Architecture Notes

- **Block-based:** Pages are lists of JSON blocks `{id, type, category, content, settings, order}`
- **Dual storage:** PostgreSQL for structured data (sites, pages), MongoDB for block JSON content
- **API switching:** `VITE_USE_MOCK=true` uses mock data, `false` uses real FastAPI backend
- **Auth is external:** JWT token from parent project (app.akm-advisor.com), validated in backend
- **Device preview:** Desktop (1200px), Tablet (768px), Mobile (375px)
- **Undo/Redo:** 50-entry history stack in editorStore
- **Auto-save:** Every 5 seconds when dirty (composable)
- **Publish:** Celery task generates static HTML from block content

## Logs API (for Agent / Debugging)

Server logs are available via REST API at `/api/v1/logs`. Supports both JWT auth and Agent API key.

### Quick Reference (copy-paste ready)

Agent key and base URL are in `.env.agent` file. Read the key before making requests:

```bash
# 1. Read agent key
AGENT_KEY=$(grep 'AGENT_API_KEY=' .env.agent | cut -d= -f2)

# 2. Application Python logs (certbot, errors, startup) — MOST USEFUL
curl -s -H "X-Agent-Key: $AGENT_KEY" \
  'https://builder.akm-advisor.com/api/v1/logs/app?tail=100' | python3 -m json.tool

# 3. App logs filtered by errors only
curl -s -H "X-Agent-Key: $AGENT_KEY" \
  'https://builder.akm-advisor.com/api/v1/logs/app?level=ERROR&tail=50' | python3 -m json.tool

# 4. App logs filtered by keyword (e.g. ssl, certbot, domain)
curl -s -H "X-Agent-Key: $AGENT_KEY" \
  'https://builder.akm-advisor.com/api/v1/logs/app?search=ssl&tail=100' | python3 -m json.tool

# 5. Docker container logs (api, nginx, postgres, mongodb, redis, worker, frontend)
curl -s -H "X-Agent-Key: $AGENT_KEY" \
  'https://builder.akm-advisor.com/api/v1/logs/api?tail=100' | python3 -m json.tool

# 6. Nginx logs with search
curl -s -H "X-Agent-Key: $AGENT_KEY" \
  'https://builder.akm-advisor.com/api/v1/logs/nginx?tail=100&search=error' | python3 -m json.tool

# 7. List all available services
curl -s -H "X-Agent-Key: $AGENT_KEY" \
  'https://builder.akm-advisor.com/api/v1/logs' | python3 -m json.tool
```

### How It Works

- **`/api/v1/logs/app`** reads from `/tmp/app.log` (RotatingFileHandler in `main.py`). Contains all Python/uvicorn/certbot logs. Works without docker CLI.
- **`/api/v1/logs/{service}`** reads Docker container logs via `curl --unix-socket /var/run/docker.sock` (docker CLI not installed in container, uses Docker HTTP API as fallback).
- Auth: Agent key from `.env.agent` is validated via parent project API `app.akm-advisor.com/api/v1/agent/{project_id}/context`.

### Authentication

Three methods are supported:
1. **Parent project agent key:** `X-Agent-Key: agent_...` — validated via `app.akm-advisor.com` (primary method)
2. **Local Agent API key:** `X-Agent-Key: <key>` — matches `AGENT_API_KEY` in server `.env`
3. **JWT Bearer token:** `Authorization: Bearer <jwt_token>`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/logs` | List available services |
| GET | `/api/v1/logs/app` | Application Python/uvicorn logs from file |
| GET | `/api/v1/logs/{service}` | Docker container logs for a service |

**Available services:** `api`, `worker`, `postgres`, `mongodb`, `redis`, `nginx`, `frontend`

### Query Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| tail | int | 100 | Number of last lines (1–5000) |
| search | string | — | Filter lines containing text (case-insensitive) |
| level | string | — | Filter by log level: ERROR, WARNING, INFO, DEBUG (`/app` only) |
| since | string | — | Docker time filter, e.g. `1h`, `30m` (`/{service}` only) |

## Dev Server

Port: **10669** (configured in `vite.config.ts`)

## Agent Rules

⚠️ **IMPORTANT: Git Commit Policy**

**NEVER commit or push changes directly to the repository.**

When code changes are needed:
1. Make the changes locally
2. Show the diff or explain what was changed
3. Wait for user confirmation
4. **User will commit and push manually**

The only exception: emergency hotfixes explicitly requested by the user with "commit this now" or similar urgent language.

This rule exists because:
- User needs to review changes before they go to production
- Commits should have meaningful messages crafted by the user
- Agent may bundle unrelated changes together
- Production deployment requires manual approval
