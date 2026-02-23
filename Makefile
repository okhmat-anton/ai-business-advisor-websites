.PHONY: dev build install clean lint preview update stop help \
       docker-up docker-down docker-build docker-logs docker-status docker-clean \
       backend-dev backend-install migrate deploy deploy-prod

# Detect docker compose command
COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

# Default target
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================
# Frontend
# ============================================

install: ## Install frontend dependencies
	cd frontend && npm install

stop: ## Stop running dev servers
	@-lsof -ti :10669 | xargs kill -9 2>/dev/null || true
	@-lsof -ti :8000 | xargs kill -9 2>/dev/null || true
	@echo "Stopped previous dev servers"

dev: stop ## Start frontend dev server (port 10669)
	cd frontend && npm run dev

build: ## Build frontend for production
	cd frontend && npm run build

preview: ## Preview production build
	cd frontend && npm run preview

lint: ## Lint frontend code
	cd frontend && npx vue-tsc --noEmit

clean: ## Remove build artifacts
	rm -rf frontend/dist frontend/node_modules/.tmp

update: ## Git pull, install deps, rebuild and restart dev server
	git pull
	cd frontend && npm install
	cd frontend && npm run build
	$(MAKE) dev

# ============================================
# Backend
# ============================================

backend-install: ## Install backend Python dependencies
	cd backend && pip install -r requirements.txt

backend-dev: ## Start backend dev server (port 8000)
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

# ============================================
# Docker
# ============================================

docker-up: ## Start all services in Docker (development)
	$(COMPOSE) up -d --build

docker-down: ## Stop all Docker services
	$(COMPOSE) down

docker-build: ## Build Docker images
	$(COMPOSE) build

docker-logs: ## View Docker logs (usage: make docker-logs or make docker-logs SVC=api)
	$(COMPOSE) logs -f $(SVC)

docker-status: ## Show Docker service status
	$(COMPOSE) ps

docker-clean: ## Stop and remove all containers, volumes, and data
	$(COMPOSE) down -v --remove-orphans

# ============================================
# Deploy
# ============================================

deploy: ## Deploy development environment
	./deploy.sh dev

deploy-prod: ## Deploy production environment
	./deploy.sh prod
