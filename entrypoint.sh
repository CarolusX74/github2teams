FROM python:3.11-slim

LABEL maintainer="Carlos Javier Torres Pensa <carlosjtp.777@gmail.com>"
LABEL description="A self-hosted FastAPI bridge between GitHub Webhooks and Microsoft Teams."

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código y configuración base
COPY app ./app
COPY data/config.json /default-config.json

# Copiar entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Usar entrypoint personalizado
ENTRYPOINT ["/entrypoint.sh"]
