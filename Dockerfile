# Dockerfile
FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Paquetes del sistema para numpy/pandas y libs comunes en ARM
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    libatlas-base-dev \
    libssl-dev \
    libffi-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Usuario no root
RUN useradd -ms /bin/bash appuser
WORKDIR /app

# Instalar deps Python primero para cache
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar código
COPY . /app

# Preparar directorios de runtime
RUN mkdir -p /app/media /app/logs && chown -R appuser:appuser /app
USER appuser

ENV DJANGO_SETTINGS_MODULE=core_config.settings
EXPOSE 8001

# Comando por defecto: migrar y levantar devserver en 8001
CMD sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8001"
