# Build stage: Usar imagen oficial de Python
FROM python:3.12-slim

# Instalar uv para gestión de dependencias ultra-rápida
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Directorio de trabajo
WORKDIR /app

# Copia de archivos de configuración
COPY pyproject.toml uv.lock ./

# Instalar dependencias sin instalar el proyecto local (cache optimizado)
RUN uv sync --frozen --no-install-project

# Copiar el código fuente
COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# Variables de entorno para producción
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Comando de ejecución con múltiples workers para paralelismo (Polars optimizado)
# Se usa 'uv run' para asegurar el uso del venv gestionado por uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
