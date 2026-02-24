#!/bin/bash
# ============================================
# Setup domain + HTTPS (Let's Encrypt)
# ============================================
# Usage:
#   ./setup-domain.sh                  # interactive prompt
#   ./setup-domain.sh builder.example.com  # pass domain as argument

set -e

# Determine docker compose command
if docker compose version &>/dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE="docker-compose"
fi

# Get domain
DOMAIN="${1}"
if [ -z "$DOMAIN" ]; then
    read -p "Enter your domain (e.g. builder.example.com): " DOMAIN
fi

if [ -z "$DOMAIN" ]; then
    echo "Error: domain is required"
    exit 1
fi

echo ""
echo "================================================"
echo "  Setting up HTTPS for: $DOMAIN"
echo "================================================"
echo ""

# --------------------------------------------------
# 0. Pre-flight checks
# --------------------------------------------------

# Check DNS resolves
echo "[1/8] Checking DNS for $DOMAIN..."
RESOLVED_IP=$(dig +short "$DOMAIN" 2>/dev/null | tail -1)
if [ -z "$RESOLVED_IP" ]; then
    echo ""
    echo "ERROR: DNS for $DOMAIN does not resolve!"
    echo ""
    echo "Add an A-record at your DNS provider:"
    echo "  Type:  A"
    echo "  Name:  $(echo "$DOMAIN" | cut -d. -f1)"
    echo "  Value: $(curl -s --max-time 3 ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
    echo "  TTL:   300"
    echo ""
    echo "Wait a few minutes for DNS to propagate, then run again."
    exit 1
fi

# Check DNS points to this server
MY_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || curl -s --max-time 5 icanhazip.com 2>/dev/null || echo "")
if [ -n "$MY_IP" ] && [ "$RESOLVED_IP" != "$MY_IP" ]; then
    echo ""
    echo "WARNING: $DOMAIN resolves to $RESOLVED_IP but this server's IP is $MY_IP"
    echo "Make sure the A-record points to this server."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo "  DNS OK: $DOMAIN → $RESOLVED_IP"

# --------------------------------------------------
# 1. Install certbot if missing
# --------------------------------------------------
echo "[2/8] Checking Certbot..."
if ! command -v certbot &>/dev/null; then
    echo "  Installing Certbot..."
    if command -v amazon-linux-extras &>/dev/null; then
        sudo amazon-linux-extras install epel -y
        sudo yum install -y certbot
    elif command -v apt-get &>/dev/null; then
        sudo apt-get update && sudo apt-get install -y certbot
    else
        echo "Error: cannot install certbot — install it manually"
        exit 1
    fi
fi
echo "  Certbot OK"

# --------------------------------------------------
# 2. Free port 80
# --------------------------------------------------
echo "[3/8] Freeing port 80..."
$COMPOSE stop nginx 2>/dev/null || true
# Kill anything else on port 80
sudo fuser -k 80/tcp 2>/dev/null || true
sleep 1

# Verify port 80 is free
if sudo lsof -i :80 -sTCP:LISTEN 2>/dev/null | grep -q LISTEN; then
    echo "ERROR: Port 80 is still in use. Stop the process and run again."
    sudo lsof -i :80 -sTCP:LISTEN
    exit 1
fi
echo "  Port 80 free"

# --------------------------------------------------
# 3. Check port 80 is reachable from outside
# --------------------------------------------------
echo "[4/8] Verifying port 80 is open in firewall..."
echo "  (if this hangs, port 80 is blocked in Lightsail firewall)"

# --------------------------------------------------
# 4. Get SSL certificate
# --------------------------------------------------
echo "[5/8] Requesting SSL certificate from Let's Encrypt..."
echo ""

# Run certbot (show output for debugging)
if ! sudo certbot certonly --standalone \
    --non-interactive --agree-tos \
    --register-unsafely-without-email \
    -d "$DOMAIN"; then
    echo ""
    echo "================================================================"
    echo "  ERROR: Certbot failed to obtain certificate!"
    echo ""
    echo "  Common causes:"
    echo "  1. Port 80 not open in Lightsail firewall (Networking tab)"
    echo "  2. DNS not pointing to this server"
    echo "     Domain resolves to: $RESOLVED_IP"
    echo "     This server IP:     $MY_IP"
    echo "  3. Domain doesn't exist yet"
    echo ""
    echo "  Fix the issue and run:  make add-domain DOMAIN=$DOMAIN"
    echo "================================================================"
    # Restart nginx on HTTP so site is accessible
    echo "Restarting nginx on HTTP..."
    $COMPOSE -f docker-compose.yml -f docker-compose.prod.yml up -d nginx 2>/dev/null || true
    exit 1
fi

CERT_DIR="/etc/letsencrypt/live/$DOMAIN"

if [ ! -f "$CERT_DIR/fullchain.pem" ]; then
    echo ""
    echo "ERROR: Certificate file not found at $CERT_DIR/fullchain.pem"
    echo "Check certbot output above."
    # Restart nginx on HTTP
    $COMPOSE -f docker-compose.yml -f docker-compose.prod.yml up -d nginx 2>/dev/null || true
    exit 1
fi

echo ""
echo "  Certificate obtained: $CERT_DIR"

# --------------------------------------------------
# 5. Update docker-compose.prod.yml — add SSL volumes/ports
# --------------------------------------------------
echo "[6/8] Updating docker-compose.prod.yml..."

if ! grep -q "letsencrypt" docker-compose.prod.yml 2>/dev/null; then
    # Rewrite nginx section with SSL support
    # Use Python for reliable YAML manipulation
    python3 - "$DOMAIN" <<'PYEOF'
import sys

domain = sys.argv[1]
with open("docker-compose.prod.yml", "r") as f:
    content = f.read()

# Check if nginx section already has ports/volumes
if "letsencrypt" not in content:
    old_nginx = """  nginx:
    restart: always"""
    new_nginx = """  nginx:
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro"""
    content = content.replace(old_nginx, new_nginx)
    with open("docker-compose.prod.yml", "w") as f:
        f.write(content)
    print("  Added SSL ports and letsencrypt volume")
PYEOF
else
    echo "  docker-compose.prod.yml already has letsencrypt config"
fi

# --------------------------------------------------
# 6. Generate nginx SSL config
# --------------------------------------------------
echo "[7/8] Writing nginx SSL config..."

CONF_FILE="nginx/conf.d/default.conf"

# Backup current config
cp "$CONF_FILE" "${CONF_FILE}.bak" 2>/dev/null || true

cat > "$CONF_FILE" <<NGINX
# Auto-generated by setup-domain.sh for $DOMAIN
# Backup saved as default.conf.bak

upstream api_backend {
    server api:8000;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name $DOMAIN _;
    return 301 https://$DOMAIN\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate     /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # API proxy
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    # Uploaded files
    location /uploads/ {
        alias /app/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Published sites
    location /published/ {
        alias /app/published/;
        expires 1h;
        add_header Cache-Control "public";
    }

    # Frontend (SPA)
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /usr/share/nginx/html;
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files \$uri =404;
    }
}
NGINX

echo "  Nginx config: $CONF_FILE"

# --------------------------------------------------
# 7. Update CORS in .env
# --------------------------------------------------
if [ -f .env ]; then
    if ! grep -q "$DOMAIN" .env; then
        sed -i.bak "s|CORS_ORIGINS=.*|CORS_ORIGINS=[\"https://$DOMAIN\",\"https://app.akm-advisor.com\"]|" .env
        rm -f .env.bak
        echo "  Updated CORS_ORIGINS in .env"
    fi
fi

# --------------------------------------------------
# 8. Rebuild and start
# --------------------------------------------------
echo "[8/8] Starting services with HTTPS..."
$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml up -d --build nginx

# --------------------------------------------------
# 9. Auto-renewal cron
# --------------------------------------------------
CRON_CMD="0 3 1 */2 * certbot renew --pre-hook \"cd $(pwd) && $COMPOSE stop nginx\" --post-hook \"cd $(pwd) && $COMPOSE start nginx\""

if ! sudo crontab -l 2>/dev/null | grep -q "certbot renew"; then
    (sudo crontab -l 2>/dev/null; echo "$CRON_CMD") | sudo crontab -
    echo "  Auto-renewal cron added"
fi

echo ""
echo "================================================"
echo "  HTTPS setup complete!"
echo ""
echo "  https://$DOMAIN"
echo ""
echo "  Certificate:  $CERT_DIR"
echo "  Auto-renewal: cron every 2 months"
echo "================================================"
