#!/bin/bash
# ============================================
# Setup domain + HTTPS (Let's Encrypt)
# ============================================
# Usage:
#   ./setup-domain.sh builder.akm-advisor.com
#   make add-domain DOMAIN=builder.akm-advisor.com

set -e

# ==================== Config ====================

DOMAIN="${1}"
if [ -z "$DOMAIN" ]; then
    read -p "Enter your domain (e.g. builder.example.com): " DOMAIN
fi
if [ -z "$DOMAIN" ]; then
    echo "Error: domain is required"
    exit 1
fi

# Detect docker compose command
if docker compose version &>/dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE="docker-compose"
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "================================================"
echo "  Setting up HTTPS for: $DOMAIN"
echo "================================================"
echo ""

# ==================== Step 1: DNS check ====================
echo "[1/7] Checking DNS..."

# Install dig/bind-utils if missing
if ! command -v dig &>/dev/null; then
    sudo yum install -y bind-utils 2>/dev/null || sudo apt-get install -y dnsutils 2>/dev/null || true
fi

RESOLVED_IP=$(dig +short "$DOMAIN" A 2>/dev/null | grep -E '^[0-9]+\.' | head -1)
if [ -z "$RESOLVED_IP" ]; then
    # Fallback: use host command or getent
    RESOLVED_IP=$(getent ahosts "$DOMAIN" 2>/dev/null | grep -E '^[0-9]+\.' | head -1 | awk '{print $1}')
fi

# Get server's public IPv4 (force IPv4!)
MY_IP=$(curl -4 -s --max-time 5 ifconfig.me 2>/dev/null || \
        curl -4 -s --max-time 5 icanhazip.com 2>/dev/null || \
        curl -4 -s --max-time 5 api.ipify.org 2>/dev/null || \
        echo "unknown")

if [ -z "$RESOLVED_IP" ]; then
    echo "  WARNING: Cannot resolve $DOMAIN via DNS"
    echo "  Server public IP: $MY_IP"
    echo ""
    echo "  Make sure you have an A-record:"
    echo "    Type: A | Name: $(echo "$DOMAIN" | cut -d. -f1) | Value: $MY_IP"
    echo ""
    read -p "  Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
else
    echo "  $DOMAIN → $RESOLVED_IP"
    if [ "$RESOLVED_IP" != "$MY_IP" ]; then
        echo "  WARNING: Server IP is $MY_IP (mismatch!)"
        read -p "  Continue anyway? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
    else
        echo "  Server IP matches — OK"
    fi
fi

# ==================== Step 2: Install certbot ====================
echo "[2/7] Checking Certbot..."

if ! command -v certbot &>/dev/null; then
    echo "  Installing..."
    if command -v amazon-linux-extras &>/dev/null; then
        sudo amazon-linux-extras install epel -y 2>&1 | tail -1
        sudo yum install -y certbot 2>&1 | tail -1
    elif command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y certbot 2>&1 | tail -1
    else
        echo "  ERROR: Install certbot manually"
        exit 1
    fi
fi
echo "  Certbot $(certbot --version 2>&1 | head -1)"

# ==================== Step 3: Stop everything on port 80 ====================
echo "[3/7] Freeing port 80..."

# Stop ALL docker containers (not just nginx — they share the network)
$COMPOSE stop 2>/dev/null || true

# Wait for port to release
sleep 2

# Kill anything still on port 80
if command -v fuser &>/dev/null; then
    sudo fuser -k 80/tcp 2>/dev/null || true
elif command -v ss &>/dev/null; then
    PORT80_PID=$(sudo ss -tlnp sport = :80 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
    if [ -n "$PORT80_PID" ]; then
        sudo kill "$PORT80_PID" 2>/dev/null || true
    fi
fi

sleep 1

# Verify port 80 is free
if ss -tln sport = :80 2>/dev/null | grep -q ":80"; then
    echo "  ERROR: Port 80 is still in use!"
    ss -tlnp sport = :80 2>/dev/null || sudo netstat -tlnp 2>/dev/null | grep :80
    echo "  Kill the process and try again."
    exit 1
fi
echo "  Port 80 is free"

# ==================== Step 4: Get SSL certificate ====================
echo "[4/7] Requesting SSL certificate..."
echo ""

# Clean up broken previous attempts
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
if sudo test -f "/etc/letsencrypt/renewal/${DOMAIN}.conf" || sudo test -d "$CERT_DIR"; then
    if ! sudo test -f "$CERT_DIR/fullchain.pem"; then
        echo "  Cleaning incomplete previous attempt..."
        sudo certbot delete --cert-name "$DOMAIN" --non-interactive 2>/dev/null || true
        sudo rm -rf "$CERT_DIR" 2>/dev/null || true
        sudo rm -f "/etc/letsencrypt/renewal/${DOMAIN}.conf" 2>/dev/null || true
    fi
fi

# Run certbot — capture output AND show it
set +e
sudo certbot certonly \
    --standalone \
    --preferred-challenges http \
    --http-01-port 80 \
    --non-interactive \
    --agree-tos \
    --email admin@${DOMAIN#*.} \
    --no-eff-email \
    -d "$DOMAIN" \
    -v 2>&1 | tee /tmp/certbot-output.txt
CERTBOT_EXIT=$?
set -e

echo ""

# Verify certificate exists
if ! sudo test -f "$CERT_DIR/fullchain.pem"; then
    echo "================================================================"
    echo "  ERROR: SSL certificate was NOT created"
    echo ""
    echo "  Certbot exit code: $CERTBOT_EXIT"
    echo ""
    echo "  Possible causes:"
    echo "  1. Port 80 not open in Lightsail Firewall"
    echo "     → Lightsail → instance → Networking → Add rule: HTTP (80)"
    echo ""
    echo "  2. DNS not pointing here"
    echo "     → Domain: $RESOLVED_IP | Server: $MY_IP"
    echo ""
    echo "  3. Rate limit — too many attempts"
    echo "     → Wait 1 hour and try again"
    echo ""
    echo "  Debug: cat /tmp/certbot-output.txt"
    echo "  Test:  sudo certbot certonly --standalone -d $DOMAIN --dry-run"
    echo "================================================================"
    # Start services back on HTTP
    echo ""
    echo "Starting services back on HTTP..."
    $COMPOSE -f docker-compose.yml -f docker-compose.prod.yml up -d 2>/dev/null || true
    exit 1
fi

echo "  Certificate ready: $CERT_DIR"

# ==================== Step 5: Nginx SSL config ====================
echo "[5/7] Creating Nginx SSL config for domain..."

# Domain configs go to ssl-sites/ dir (included by nginx.conf automatically)
SSL_SITES_DIR="nginx/ssl-sites"
mkdir -p "$SSL_SITES_DIR"
CONF_FILE="$SSL_SITES_DIR/${DOMAIN}.conf"

cat > "$CONF_FILE" <<NGINX_TEMPLATE
# Auto-generated SSL config for ${DOMAIN}
server {
    listen 443 ssl;
    server_name ${DOMAIN};

    ssl_certificate     /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;

    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    location /uploads/ {
        alias /app/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /published/ {
        alias /app/published/;
        expires 1h;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://frontend_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        proxy_pass http://frontend_app;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# HTTP -> HTTPS redirect for ${DOMAIN}
server {
    listen 80;
    server_name ${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/acme;
        try_files \$uri =404;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}
NGINX_TEMPLATE

echo "  Written: $CONF_FILE"

# ==================== Step 6: Update .env ====================
echo "[6/7] Updating .env..."

# docker-compose.prod.yml already has port 443 and letsencrypt volume configured.
# Port 80 comes from base docker-compose.yml via NGINX_PORT in .env.
echo "  docker-compose.prod.yml — already configured (443 + letsencrypt)"

# Make sure NGINX_PORT=80 for production
if [ -f .env ]; then
    sed -i.bak "s|NGINX_PORT=.*|NGINX_PORT=80|" .env
    rm -f .env.bak
    echo "  NGINX_PORT=80 in .env"
fi

# Update CORS in .env
if [ -f .env ] && ! grep -q "$DOMAIN" .env; then
    sed -i.bak "s|CORS_ORIGINS=.*|CORS_ORIGINS=[\"https://$DOMAIN\",\"https://app.akm-advisor.com\"]|" .env
    rm -f .env.bak
    echo "  CORS_ORIGINS updated in .env"
fi

# ==================== Step 7: Start everything ====================
echo "[7/7] Starting all services..."

$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Wait and check
sleep 5
echo ""
echo "  Service status:"
$COMPOSE ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || $COMPOSE ps

# ==================== Auto-renewal cron ====================
CRON_CMD="0 3 1 */2 * certbot renew --pre-hook \"cd $PROJECT_DIR && $COMPOSE stop nginx\" --post-hook \"cd $PROJECT_DIR && $COMPOSE start nginx\" >> /var/log/certbot-renew.log 2>&1"

if ! sudo crontab -l 2>/dev/null | grep -q "certbot renew"; then
    (sudo crontab -l 2>/dev/null; echo "$CRON_CMD") | sudo crontab -
    echo ""
    echo "  Auto-renewal cron added (every 2 months)"
fi

echo ""
echo "================================================"
echo "  DONE! Site is live at:"
echo ""
echo "  https://$DOMAIN"
echo ""
echo "  SSL cert:    $CERT_DIR"
echo "  Nginx conf:  $CONF_FILE"
echo "  Renewal:     automatic (cron)"
echo "================================================"
