FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cache layer)
COPY pyproject.toml README.md .
RUN pip install --no-cache-dir -e ".[dev]"

# Copy project
COPY . .

# Collect static during deployment with the configured runtime environment.
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
ENV DJANGO_SETTINGS_MODULE=config.settings.production

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "60"]
