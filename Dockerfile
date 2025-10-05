# ==========================================
#  GitHub → Teams Bridge (github2teams)
#  Author: Carlos Javier Torres Pensa
#  © 2025 - Open Source
# ==========================================

FROM python:3.11-slim

LABEL maintainer="Carlos Javier Torres Pensa <carlosjtp.777@gmail.com>"
LABEL description="A self-hosted FastAPI bridge between GitHub Webhooks and Microsoft Teams."

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la app
COPY app ./app

# Copiar archivo(s) de configuración
COPY data/config.json ./data/config.json

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
