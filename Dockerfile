# Ultra-optimized Test Generator with Alpine Linux
FROM python:3.11-alpine

# Metadata and build args in single layer
LABEL maintainer="Test Generator" \
      version="1.0" \
      description="Generic Test Generator - Mobile-first interactive testing system"

ARG APP_USER=testapp
ARG APP_UID=1000

# Single RUN layer for system setup, user creation, dependencies, and cleanup
RUN apk add --no-cache curl sqlite && \
    addgroup -g ${APP_UID} ${APP_USER} && \
    adduser -u ${APP_UID} -G ${APP_USER} -D -h /app ${APP_USER} && \
    mkdir -p /app/tests /app/data && \
    chown -R ${APP_USER}:${APP_USER} /app

# Set working directory and user in same layer context
WORKDIR /app
USER ${APP_USER}

# Copy requirements and install Python dependencies in single layer
COPY --chown=${APP_USER}:${APP_USER} requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# Copy application files with proper ownership
COPY --chown=${APP_USER}:${APP_USER} app/ ./app/
COPY --chown=${APP_USER}:${APP_USER} templates/ ./templates/
COPY --chown=${APP_USER}:${APP_USER} question-bank-template.json test-schema.json ./

# Runtime configuration
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "app.main"]