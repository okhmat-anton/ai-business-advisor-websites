#!/bin/bash
# ============================================
# Auto-generate .env with secure random keys
# ============================================
# Generates passwords and secret keys automatically.
# Docker Compose reads the same .env file, so all
# credentials stay in sync between services.

set -e

ENV_FILE="${1:-.env}"

if [ -f "$ENV_FILE" ]; then
    echo "⚠ $ENV_FILE already exists. Skipping generation."
    echo "  Delete it first if you want to regenerate: rm $ENV_FILE"
    exit 0
fi

# Generate random strings
gen_key()   { openssl rand -hex 32; }
gen_pass()  { openssl rand -base64 24 | tr -d '/+=' | head -c 32; }

SECRET_KEY=$(gen_key)
JWT_SECRET_KEY=$(gen_key)
POSTGRES_PASSWORD=$(gen_pass)

# Detect environment: if running on EC2/Lightsail, default to production
if curl -s --max-time 1 http://169.254.169.254/latest/meta-data/instance-id &>/dev/null; then
    DEFAULT_ENV="production"
    DEFAULT_DEBUG="false"
    DEFAULT_NGINX_PORT="80"
    DEFAULT_CORS='["http://localhost"]'
else
    DEFAULT_ENV="development"
    DEFAULT_DEBUG="true"
    DEFAULT_NGINX_PORT="10669"
    DEFAULT_CORS='["http://localhost:10669","http://localhost:3000","http://localhost:8000"]'
fi

cat > "$ENV_FILE" <<EOF
# ============================================
# AKM Site Builder - Environment Configuration
# Auto-generated on $(date +%Y-%m-%d\ %H:%M:%S)
# ============================================

# App
APP_NAME=AKM Site Builder
DEBUG=${DEFAULT_DEBUG}
ENVIRONMENT=${DEFAULT_ENV}
SECRET_KEY=${SECRET_KEY}

# JWT (must match parent project app.akm-advisor.com)
# ⚠ Replace with the real key from the parent project!
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256

# PostgreSQL
# These values are used by BOTH the postgres container and the API.
# Docker Compose reads them from this file — they always stay in sync.
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=sitebuilder
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=sitebuilder_db

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=sitebuilder

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# CORS (JSON array of allowed origins)
# ⚠ For production, add your real domain: ["https://your-domain.com","https://app.akm-advisor.com"]
CORS_ORIGINS=${DEFAULT_CORS}

# File upload
MAX_UPLOAD_SIZE=104857600
UPLOAD_DIR=/app/uploads

# Publish
PUBLISH_DIR=/app/published

# Docker ports
API_PORT=8000
NGINX_PORT=${DEFAULT_NGINX_PORT}
EOF

echo "✅ Generated $ENV_FILE with secure random keys"
echo ""
echo "   SECRET_KEY:        (auto-generated)"
echo "   POSTGRES_PASSWORD: (auto-generated)"
echo "   JWT_SECRET_KEY:    (auto-generated — replace with parent project key!)"
echo "   ENVIRONMENT:       ${DEFAULT_ENV}"
echo "   NGINX_PORT:        ${DEFAULT_NGINX_PORT}"
echo ""

if [ "$DEFAULT_ENV" = "production" ]; then
    echo "⚠ Production detected. Review before starting:"
    echo "   - Set JWT_SECRET_KEY to match app.akm-advisor.com"
    echo "   - Update CORS_ORIGINS with your domain"
    echo "   nano $ENV_FILE"
fi
