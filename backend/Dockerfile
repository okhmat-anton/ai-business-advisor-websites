# ============================================
# Stage 1: Base image with system dependencies
# ============================================
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libmagic1 \
    certbot \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ============================================
# Stage 2: Install Python dependencies
# ============================================
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 3: Production image
# ============================================
FROM dependencies AS production

COPY . .

# Create upload and publish directories
RUN mkdir -p /app/uploads /app/published

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-"]

# ============================================
# Stage 4: Development image
# ============================================
FROM dependencies AS development

COPY . .

RUN mkdir -p /app/uploads /app/published

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
