# =========================================================
# Etapa 1: builder — instala dependencias de Python
# =========================================================
FROM python:3.14-slim AS builder

WORKDIR /app

# Dependencias del sistema necesarias SOLO para compilar
# (psycopg necesita libpq-dev + build-essential para compilar su parte en C)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt


# =========================================================
# Etapa 2: imagen final — liviana, sin herramientas de build
# =========================================================
FROM python:3.14-slim

# Solo la librería de runtime de Postgres (no el -dev, no compiladores)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY src/ ./src/

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

RUN mkdir -p /app/src/staticfiles \
    && chown -R appuser:appuser /app /home/appuser/.local
USER appuser

WORKDIR /app/src

EXPOSE 8000

# CMD de producción. En desarrollo, docker-compose.yml lo sobreescribe
# con "manage.py runserver" para tener autoreload.
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]