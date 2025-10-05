# ==========================================
#  GitHub → Teams Bridge (github2teams)
#  Author: Carlos Javier Torres Pensa
#  © 2025 - Open Source
# ==========================================

FROM python:3.11-slim

LABEL maintainer="Carlos Javier Torres Pensa <carlosjtp.777@gmail.com>"
LABEL description="A self-hosted FastAPI bridge between GitHub Webhooks and Microsoft Teams."

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and data
COPY app ./app
COPY data ./data

EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
