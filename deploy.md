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

### 10.2. Автоматическая настройка HTTPS

Одна команда — установит Certbot, получит сертификат, настроит Nginx и автообновление:

```bash
cd ~/ai-business-advisor-websites
make add-domain DOMAIN=builder.ваш-домен.com
```

Или без make:

```bash
./setup-domain.sh builder.ваш-домен.com
```

Скрипт автоматически:
1. Установит Certbot (если нет)
2. Остановит nginx, получит SSL-сертификат от Let's Encrypt
3. Перепишет `nginx/conf.d/default.conf` с HTTPS + редирект 80→443
4. Обновит `docker-compose.prod.yml` — добавит порт 443 и volume сертификатов
5. Обновит `CORS_ORIGINS` в `.env` с вашим доменом
6. Перезапустит nginx
7. Добавит cron для автообновления сертификатов (каждые 2 месяца)

После выполнения: `https://builder.ваш-домен.com`

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
