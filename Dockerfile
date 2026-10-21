# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Prevent Python from writing .pyc and enable buffer-less stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for compiling extensions if necessary
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run as non-root user for production container hardening
RUN useradd -m -u 1000 climasense && chown -R climasense:climasense /app
USER climasense

# Expose HTTP port
EXPOSE 5000

# Container healthcheck using the native /health route
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start app using gunicorn with eventlet for WebSockets
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:create_app('production')"]
