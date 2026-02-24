#!/bin/bash
# ============================================
# AKM Site Builder - Self-deployment script
# ============================================

set -e

echo "================================================"
echo "  AKM Site Builder - Deploy"
echo "================================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Determine docker compose command
if docker compose version &> /dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE="docker-compose"
fi

# Check .env file — auto-generate if missing
if [ ! -f .env ]; then
    echo "No .env found — generating with secure random keys..."
    bash ./generate-env.sh .env
    echo ""
    echo "⚠ Review .env before first launch (especially JWT_SECRET_KEY and CORS_ORIGINS)."
    echo "  To edit: nano .env"
    echo "  Then run this script again."
    exit 1
fi

MODE=${1:-dev}

case $MODE in
    dev)
        echo "Starting in DEVELOPMENT mode..."
        $COMPOSE up -d --build
        echo ""
        echo "Waiting for services to start..."
        sleep 5
        echo ""
        echo "Running database migrations..."
        $COMPOSE exec api alembic upgrade head 2>/dev/null || echo "Migrations skipped (tables auto-created in dev mode)"
        echo ""
        echo "================================================"
        echo "  Development environment is ready!"
        echo "  API:       http://localhost:${API_PORT:-8000}"
        echo "  API Docs:  http://localhost:${API_PORT:-8000}/api/v1/docs"
        echo "  Frontend:  Run 'cd frontend && npm run dev' separately"
        echo "  Nginx:     http://localhost:${NGINX_PORT:-10669}"
        echo "================================================"
        ;;
    prod)
        echo "Starting in PRODUCTION mode..."
        echo "Building frontend..."
        $COMPOSE -f docker-compose.yml -f docker-compose.prod.yml up -d --build
        echo ""
        echo "Waiting for services to start..."
        sleep 8
        echo ""
        echo "Running database migrations..."
        $COMPOSE exec api alembic upgrade head 2>/dev/null || echo "Migrations warning - check logs"
        echo ""
        echo "================================================"
        echo "  Production environment is ready!"
        echo "  App: http://localhost:${NGINX_PORT:-80}"
        echo "================================================"
        ;;
    stop)
        echo "Stopping all services..."
        $COMPOSE down
        echo "Done."
        ;;
    restart)
        echo "Restarting all services..."
        $COMPOSE restart
        echo "Done."
        ;;
    logs)
        $COMPOSE logs -f ${2:-}
        ;;
    status)
        $COMPOSE ps
        ;;
    clean)
        echo "⚠ This will remove all containers, volumes, and data!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            $COMPOSE down -v --remove-orphans
            echo "Cleaned."
        fi
        ;;
    *)
        echo "Usage: $0 {dev|prod|stop|restart|logs|status|clean}"
        echo ""
        echo "  dev     - Start development environment"
        echo "  prod    - Start production environment"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - View logs (optionally specify service)"
        echo "  status  - Show service status"
        echo "  clean   - Remove everything including data"
        exit 1
        ;;
esac
