# Imagen base ligera de Python
FROM python:3.11-slim

# Variables de build
ARG APP_USER=testapp
ARG APP_UID=1000

# Crear usuario no-root para seguridad
RUN groupadd -g ${APP_UID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_USER} -d /app -m -s /bin/bash ${APP_USER}

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar requirements primero para cache de Docker layers
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# Crear directorios necesarios
RUN mkdir -p /app/tests /app/data /app/logs && \
    chown -R ${APP_USER}:${APP_USER} /app

# Cambiar a usuario no-root
USER ${APP_USER}

# Puerto expuesto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicio
CMD ["python", "-m", "app.main"]