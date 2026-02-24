# Деплой на Amazon Lightsail

Пошаговая инструкция по развертыванию AKM Site Builder на Amazon Lightsail.

---

## 1. Создание инстанса в Lightsail

1. Войдите в [Amazon Lightsail](https://lightsail.aws.amazon.com/)
2. Нажмите **Create instance**
3. Настройки:
   - **Region:** выберите ближайший к пользователям (например, `eu-central-1` для Европы)
   - **Platform:** Linux/Unix
   - **Blueprint:** OS Only → **Ubuntu 22.04 LTS**
   - **Instance plan:** минимум **2 GB RAM / 1 vCPU** (рекомендуется **4 GB RAM / 2 vCPU** для продакшена)
   - **Instance name:** `site-builder`
4. Нажмите **Create instance**
5. Дождитесь статуса **Running**

---

## 2. Настройка сети (Firewall)

В разделе **Networking** инстанса откройте порты:

| Порт   | Протокол | Описание          |
|--------|----------|-------------------|
| 22     | TCP      | SSH               |
| 80     | TCP      | HTTP              |
| 443    | TCP      | HTTPS (SSL)       |
| 10669  | TCP      | Приложение (Nginx) |

> После настройки SSL и домена порт 10669 можно закрыть и использовать только 80/443.

---

## 3. Привязка статического IP

1. В Lightsail → **Networking** → **Create static IP**
2. Привяжите к инстансу `site-builder`
3. Запомните IP-адрес (далее: `YOUR_SERVER_IP`)

---

## 4. Подключение к серверу

### Через браузер
Нажмите **Connect using SSH** в панели Lightsail.

### Через терминал
Скачайте SSH-ключ из Lightsail → **Account** → **SSH keys** → **Download**:

```bash
chmod 400 ~/Downloads/LightsailDefaultKey-*.pem
ssh -i ~/Downloads/LightsailDefaultKey-*.pem ubuntu@YOUR_SERVER_IP
```

---

## 5. Установка зависимостей на сервере

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu

# Установка Docker Compose plugin
sudo apt install -y docker-compose-plugin

# Установка Git
sudo apt install -y git

# Перелогиниться для применения группы docker
exit
```

Подключитесь заново:

```bash
ssh -i ~/Downloads/LightsailDefaultKey-*.pem ubuntu@YOUR_SERVER_IP
```

Проверьте установку:

```bash
docker --version          # Docker version 24.x+
docker compose version    # Docker Compose version v2.x+
git --version             # git version 2.x+
```

---

## 6. Генерация SSH-ключа и добавление в GitHub

### 6.1. Генерация ключа на сервере

```bash
ssh-keygen -t ed25519 -C "site-builder-lightsail"
```

Нажимайте **Enter** на все вопросы (без пароля).

### 6.2. Копирование публичного ключа

```bash
cat ~/.ssh/id_ed25519.pub
```

Скопируйте весь вывод (начинается с `ssh-ed25519 ...`).

### 6.3. Добавление ключа в GitHub

1. Откройте [GitHub → Settings → SSH and GPG keys](https://github.com/settings/keys)
2. Нажмите **New SSH key**
3. Заполните:
   - **Title:** `Lightsail Site Builder` (любое описание)
   - **Key type:** Authentication Key
   - **Key:** вставьте скопированный ключ
4. Нажмите **Add SSH key**

### 6.4. Проверка подключения

```bash
ssh -T git@github.com
```

Ожидаемый ответ:
```
Hi okhmat-anton! You've been successfully authenticated, but GitHub does not provide shell access.
```

> **Если репозиторий приватный** — можно также добавить ключ как **Deploy Key** в настройках конкретного репо:
> `GitHub → okhmat-anton/ai-business-advisor-websites → Settings → Deploy keys → Add deploy key`

---

## 7. Клонирование репозитория

```bash
cd /home/ubuntu
git clone git@github.com:okhmat-anton/ai-business-advisor-websites.git
cd ai-business-advisor-websites
```

---

## 8. Настройка переменных окружения

```bash
cp .env.example .env
nano .env
```

Измените следующие значения:

```env
# ОБЯЗАТЕЛЬНО замените на надежные случайные строки
SECRET_KEY=ваш_сложный_случайный_ключ_64_символа
JWT_SECRET_KEY=ключ_из_основного_проекта_akm_advisor

# Пароль от PostgreSQL — задайте свой
POSTGRES_PASSWORD=ваш_надежный_пароль_бд

# Для продакшена
DEBUG=false
ENVIRONMENT=production

# CORS — укажите домен
CORS_ORIGINS=["https://ваш-домен.com","https://app.akm-advisor.com"]

# Порты (по умолчанию ОК)
API_PORT=8000
NGINX_PORT=10669
```

Для генерации случайного ключа:

```bash
openssl rand -hex 32
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`.

---

## 9. Запуск в продакшене

```bash
# Сборка и запуск всех контейнеров
./deploy.sh prod
```

Или вручную:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Дождитесь запуска (1-2 минуты) и проверьте:

```bash
# Статус контейнеров
docker compose ps

# Логи (если что-то не работает)
docker compose logs -f
```

Все контейнеры должны быть в статусе `Up (healthy)`:

```
sb-postgres   ✓ healthy
sb-mongodb    ✓ healthy
sb-redis      ✓ healthy
sb-api        ✓ running
sb-worker     ✓ running
sb-nginx      ✓ running
```

### Проверка работоспособности

```bash
# API
curl http://localhost:8000/api/v1/docs

# Nginx (фронтенд)
curl -I http://localhost:10669
```

Из браузера: `http://YOUR_SERVER_IP:10669`

---

## 10. Настройка домена (опционально)

### 10.1. DNS

Добавьте A-запись в DNS-провайдере:

```
Type: A
Name: builder (или @ для корневого домена)
Value: YOUR_SERVER_IP
TTL: 300
```

### 10.2. SSL с Let's Encrypt (Certbot)

```bash
# Установка Certbot
sudo apt install -y certbot

# Остановить Nginx контейнер для получения сертификата
docker compose stop nginx

# Получение сертификата
sudo certbot certonly --standalone -d builder.ваш-домен.com

# Запустить обратно
docker compose start nginx
```

Для автообновления сертификатов добавьте cron:

```bash
sudo crontab -e
```

Добавьте строку:

```
0 3 * * * certbot renew --pre-hook "cd /home/ubuntu/ai-business-advisor-websites && docker compose stop nginx" --post-hook "cd /home/ubuntu/ai-business-advisor-websites && docker compose start nginx"
```

> **Для полноценного SSL** нужно обновить `nginx/conf.d/default.conf` — добавить секцию с listen 443, ssl_certificate и редирект с 80 на 443.

---

## 11. Обновление приложения

При пуше нового кода в репозиторий, на сервере выполните:

```bash
cd /home/ubuntu/ai-business-advisor-websites
git pull origin main
./deploy.sh prod
```

Или одной командой:

```bash
cd /home/ubuntu/ai-business-advisor-websites && git pull && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 12. Полезные команды

```bash
# Просмотр логов конкретного сервиса
docker compose logs -f api        # Backend
docker compose logs -f nginx      # Nginx
docker compose logs -f worker     # Celery worker
docker compose logs -f postgres   # PostgreSQL

# Перезапуск одного сервиса
docker compose restart api

# Зайти в контейнер
docker compose exec api bash
docker compose exec postgres psql -U sitebuilder -d sitebuilder_db

# Бэкап базы данных
docker compose exec postgres pg_dump -U sitebuilder sitebuilder_db > backup_$(date +%Y%m%d).sql

# Восстановление бэкапа
cat backup_20260223.sql | docker compose exec -T postgres psql -U sitebuilder -d sitebuilder_db

# Очистка Docker (освобождение места)
docker system prune -af

# Статус диска
df -h
```

---

## 13. Мониторинг и автозапуск

Docker-контейнеры настроены с `restart: always` в продакшене — они автоматически перезапускаются после перезагрузки сервера.

Убедитесь, что Docker стартует при загрузке:

```bash
sudo systemctl enable docker
```

---

## Структура контейнеров

```
┌─────────────────────────────────────────────┐
│              Amazon Lightsail               │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Nginx   │  │ FastAPI  │  │  Celery   │  │
│  │ :10669  │──│  :8000   │  │  Worker   │  │
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
| `Permission denied` при git clone | Проверьте SSH-ключ в GitHub (шаг 6) |
| Контейнер `api` падает | `docker compose logs api` — проверить ошибки |
| Не подключается к БД | Проверить `POSTGRES_HOST=postgres` в `.env` |
| Порт 10669 недоступен | Проверить Firewall в Lightsail (шаг 2) |
| Мало памяти | Увеличить swap: `sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile` |
| Docker permission denied | `sudo usermod -aG docker ubuntu` и перелогиниться |
