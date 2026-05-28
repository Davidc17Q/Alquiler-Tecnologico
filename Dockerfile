# Imagen del monolito Django — Clean Architecture
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# gettext para compilar traducciones i18n (.po → .mo)
RUN apt-get update && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/scripts/docker-entrypoint.sh \
    && python manage.py compilemessages || true

EXPOSE 8000

CMD ["/app/scripts/docker-entrypoint.sh"]
