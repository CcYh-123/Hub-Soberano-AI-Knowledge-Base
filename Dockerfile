# Dockerfile for Antigravity Backend (FastAPI)
# Target: Google Cloud Run

FROM python:3.11-slim

# Evitar la creación de archivos .pyc y habilitar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependencias de sistema necesarias (si las hay)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Exponer el puerto que usará Cloud Run (por defecto 8080)
EXPOSE 8080

# Comando para ejecutar la aplicación
# Usamos uvicorn directamente llamando al script de bridge
CMD ["python", "scripts/api_bridge.py"]
