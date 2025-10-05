# ==========================================
#  GitHub → Teams Bridge (github2teams)
#  Author: Carlos Javier Torres Pensa
#  © 2025 - Open Source
# ==========================================

FROM python:3.11-slim

LABEL maintainer="Carlos Javier Torres Pensa <carlosjtp.777@gmail.com>"
LABEL description="A self-hosted FastAPI bridge between GitHub Webhooks and Microsoft Teams."

# Evitar buffering en logs de Python
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente de la app
COPY app ./app

# Copiar archivo de configuración por defecto a la raíz del contenedor
COPY data/config.json /default-config.json

# Copiar script de arranque con permisos de ejecución
COPY --chmod=755 entrypoint.sh /entrypoint.sh

# Exponer el puerto de FastAPI
EXPOSE 8000

# Ejecutar el script de arranque personalizado
ENTRYPOINT ["/entrypoint.sh"]
