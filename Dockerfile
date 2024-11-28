FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=backend.settings

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create supervisor configuration and log directory with correct permissions
RUN mkdir -p /var/log/supervisor && \
    mkdir -p /var/run/supervisor && \
    chmod -R 777 /var/log/supervisor /var/run/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]