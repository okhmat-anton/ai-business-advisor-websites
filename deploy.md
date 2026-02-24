# Деплой на Amazon Lightsail

> **Локальная разработка** — `make dev` запускает Vite на порту **10669**.  
> **Продакшен (Lightsail)** — Nginx на стандартных портах **80/443**.

---

## 1. Создание инстанса

1. Откройте [Amazon Lightsail](https://lightsail.aws.amazon.com/)
2. **Create instance**
3. Настройки:
   - **Region:** ближайший к пользователям (например `eu-central-1`)
   - **Platform:** Linux/Unix
   - **Blueprint:** OS Only → **Amazon Linux 2**
   - **Plan:** минимум **2 GB RAM / 1 vCPU** (рекомендуется 4 GB для прода)
   - **Name:** `site-builder`
4. **Create instance** → дождитесь статуса **Running**

---

## 2. Firewall

В разделе **Networking** инстанса откройте порты:

| Порт | Протокол | Описание |
|------|----------|----------|
| 22   | TCP      | SSH      |
| 80   | TCP      | HTTP     |
| 443  | TCP      | HTTPS    |

---

## 3. Статический IP

1. Lightsail → **Networking** → **Create static IP**
2. Привяжите к инстансу `site-builder`
3. Запомните IP (далее: `YOUR_SERVER_IP`)

---

## 4. Подключение к серверу

### Через браузер
Нажмите **Connect using SSH** в панели Lightsail.

### Через терминал

Скачайте ключ: Lightsail → **Account** → **SSH keys** → **Download**

```bash
chmod 400 ~/Downloads/LightsailDefaultKey-*.pem
ssh -i ~/Downloads/LightsailDefaultKey-*.pem ec2-user@YOUR_SERVER_IP
```

---

## 5. Установка зависимостей

```bash
# Обновление системы
sudo yum update -y

# Docker
sudo amazon-linux-extras install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Docker Compose v2 (plugin)
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Git
sudo yum install -y git

# Make (для Makefile)
sudo yum install -y make

# Перелогиниться (применить группу docker)
exit
```

Подключитесь заново и проверьте:

```bash
ssh -i ~/Downloads/LightsailDefaultKey-*.pem ec2-user@YOUR_SERVER_IP

docker --version          # Docker version 20.x+
docker compose version    # Docker Compose version v2.x+
git --version
```

---

## 6. SSH-ключ для GitHub

### 6.1. Генерация ключа на сервере

```bash
ssh-keygen -t rsa -b 4096 -C "site-builder-lightsail"
cat ~/.ssh/id_rsa.pub
```

Скопируйте **всю строку целиком** — начинается с `ssh-rsa AAAA...` и заканчивается `site-builder-lightsail`.

> При копировании через браузерный SSH-терминал Lightsail убедитесь, что нет переносов строк и лишних пробелов. Ключ — **одна непрерывная строка**.

### 6.3. Добавление в GitHub

1. Откройте [GitHub → Settings → SSH and GPG keys](https://github.com/settings/keys)
2. **New SSH key**
3. Заполните:
   - **Title:** `Lightsail Site Builder`
   - **Key type:** Authentication Key
   - **Key:** вставьте скопированный ключ
4. **Add SSH key**

> Для приватного репо можно вместо этого использовать **Deploy Key**:
> `GitHub → okhmat-anton/ai-business-advisor-websites → Settings → Deploy keys → Add deploy key`

### 6.4. Проверка

```bash
ssh -T git@github.com
```

Ответ: `Hi okhmat-anton! You've successfully authenticated...`

---

## 7. Клонирование репозитория

```bash
cd ~
git clone git@github.com:okhmat-anton/ai-business-advisor-websites.git
cd ai-business-advisor-websites
```

---

## 8. Настройка .env

`.env` генерируется **автоматически** при первом запуске `deploy.sh`. Все пароли и ключи создаются случайными и сразу совпадают с тем, что используют Docker-контейнеры (PostgreSQL, API и т.д.).

```bash
chmod +x deploy.sh generate-env.sh
./deploy.sh prod
```

При первом запуске скрипт:
1. Обнаружит отсутствие `.env`
2. Вызовет `generate-env.sh` — сгенерирует `SECRET_KEY`, `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`
3. На сервере (EC2/Lightsail) автоматически выставит `ENVIRONMENT=production`, `NGINX_PORT=80`
4. Остановится и попросит проверить файл

Проверьте и при необходимости отредактируйте:

```bash
nano .env
```

Что стоит поправить:
- **`JWT_SECRET_KEY`** — замените на ключ из основного проекта `app.akm-advisor.com`
- **`CORS_ORIGINS`** — добавьте ваш домен: `["https://ваш-домен.com","https://app.akm-advisor.com"]`

> Остальные значения (пароли БД, секреты) уже сгенерированы и совпадают с Docker.

После проверки запустите `./deploy.sh prod` повторно.

Сохранить: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 9. Запуск

```bash
./deploy.sh prod
```

Или вручную:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Проверка:

```bash
# Статус контейнеров
docker compose ps

# Логи
docker compose logs -f

# HTTP
curl -I http://localhost
```

Все сервисы должны быть `Up`:

```
sb-postgres   ✓ healthy
sb-mongodb    ✓ healthy
sb-redis      ✓ healthy
sb-api        ✓ running
sb-worker     ✓ running
sb-nginx      ✓ running
```

Из браузера: `http://YOUR_SERVER_IP`

---

## 10. Домен и SSL

### 10.1. DNS

Добавьте A-запись у DNS-провайдера:

```
Type:  A
Name:  builder  (или @ для корневого)
Value: YOUR_SERVER_IP
TTL:   300
```

Проверка: `dig +short builder.ваш-домен.com`

### 10.2. Получение SSL-сертификата

```bash
# Установка Certbot
sudo amazon-linux-extras install epel -y
sudo yum install -y certbot

# Освободить порт 80
cd ~/ai-business-advisor-websites
docker compose stop nginx

# Получить сертификат
sudo certbot certonly --standalone -d builder.ваш-домен.com

# Пути к сертификатам:
#   /etc/letsencrypt/live/builder.ваш-домен.com/fullchain.pem
#   /etc/letsencrypt/live/builder.ваш-домен.com/privkey.pem
```

### 10.3. Настройка Nginx для SSL

Обновите `docker-compose.prod.yml` — добавьте сертификаты и порт 443:

```yaml
  nginx:
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
```

Замените `nginx/conf.d/default.conf`:

```nginx
upstream api_backend {
    server api:8000;
}

# HTTP → HTTPS редирект
server {
    listen 80;
    server_name builder.ваш-домен.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name builder.ваш-домен.com;

    ssl_certificate     /etc/letsencrypt/live/builder.ваш-домен.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/builder.ваш-домен.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location /uploads/ {
        alias /app/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /published/ {
        alias /app/published/;
        expires 1h;
    }

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /usr/share/nginx/html;
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }
}
```

Перезапустить:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build nginx
```

### 10.4. Автообновление сертификатов

```bash
sudo crontab -e
```

Добавить:

```
0 3 1 */2 * certbot renew --pre-hook "cd ~/ai-business-advisor-websites && docker compose stop nginx" --post-hook "cd ~/ai-business-advisor-websites && docker compose start nginx"
```

---

## 11. Обновление приложения

```bash
cd ~/ai-business-advisor-websites
git pull origin main
./deploy.sh prod
```

---

## 12. Полезные команды

```bash
# Логи
docker compose logs -f api
docker compose logs -f nginx
docker compose logs -f worker

# Перезапуск сервиса
docker compose restart api

# Зайти в контейнер
docker compose exec api bash
docker compose exec postgres psql -U sitebuilder -d sitebuilder_db

# Бэкап БД
docker compose exec postgres pg_dump -U sitebuilder sitebuilder_db > backup_$(date +%Y%m%d).sql

# Восстановление
cat backup.sql | docker compose exec -T postgres psql -U sitebuilder -d sitebuilder_db

# Очистка Docker
docker system prune -af

# Диск
df -h
```

---

## 13. Автозапуск

Docker уже настроен на автозапуск (`systemctl enable docker`).
Контейнеры с `restart: always` перезапускаются автоматически после перезагрузки сервера.

---

## Архитектура

```
┌─────────────────────────────────────────────┐
│              Amazon Lightsail               │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Nginx   │  │ FastAPI  │  │  Celery   │  │
│  │ :80/443 │──│  :8000   │  │  Worker   │  │
│  └─────────┘  └──────────┘  └───────────┘  │
│       │            │  │           │         │
│  ┌────┴──┐    ┌────┴──┴───┐  ┌───┴──┐      │
│  │ Front │    │ PostgreSQL│  │Redis │      │
│  │ (SPA) │    │  :5432    │  │:6379 │      │
│  └───────┘    └───────────┘  └──────┘      │
│                    │                        │
│               ┌────┴─────┐                  │
│               │ MongoDB  │                  │
│               │  :27017  │                  │
│               └──────────┘                  │
└─────────────────────────────────────────────┘
```

---

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| `Permission denied (publickey)` при git clone | SSH-ключ не добавлен в GitHub — шаг 6 |
| `Key is invalid` в GitHub | Используйте RSA: `ssh-keygen -t rsa -b 4096`, копируйте `id_rsa.pub` одной строкой без переносов |
| Контейнер `api` падает | `docker compose logs api` |
| Не подключается к БД | `POSTGRES_HOST=postgres` в `.env` |
| Сайт не открывается | Firewall в Lightsail (шаг 2), `NGINX_PORT=80` в `.env` |
| Мало памяти | `sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile` |
| `docker: permission denied` | `sudo usermod -aG docker ec2-user` и перелогиниться |
| `docker compose` не найден | Переустановить plugin — шаг 5 |
