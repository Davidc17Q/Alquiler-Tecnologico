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

RUN python manage.py compilemessages || true

EXPOSE 8000

# Migraciones y servidor de desarrollo (Compose puede sobreescribir el comando)
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
