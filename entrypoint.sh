#!/bin/sh
set -e

# ==========================================
#  GitHub → Teams Bridge (github2teams)
#  Entrypoint Script
#  © 2025 - Carlos Javier Torres Pensa
# ==========================================

mkdir -p /app/data

if [ ! -f /app/data/config.json ]; then
    echo "📄 [$(date)] Config no encontrado, copiando config por defecto al volumen..."
    cp /default-config.json /app/data/config.json || {
        echo "❌ Error: No se pudo copiar /default-config.json a /app/data/config.json"
        ls -l / /app || true
        exit 1
    }
else
    echo "✅ [$(date)] Config existente detectado, se mantiene."
fi

echo "🚀 Iniciando FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
