# Multi-stage build for Matrix Display Application

# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /build

# Copy package files
COPY web/package*.json ./
RUN npm install

# Copy source and build
COPY web/ ./
RUN npm run build

# Stage 2: Python Application
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    cython3 \
    && rm -rf /var/lib/apt/lists/*

# Install rpi-rgb-led-matrix manually (required for hardware control)
RUN git clone https://github.com/hzeller/rpi-rgb-led-matrix.git /opt/rpi-rgb-led-matrix \
    && cd /opt/rpi-rgb-led-matrix/bindings/python \
    && make build-python PYTHON=$(which python3) \
    && make install-python PYTHON=$(which python3)

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY data/ ./data/
COPY scenes/ ./scenes/
COPY emulator_config.json ./

# Copy built frontend from stage 1
COPY --from=frontend-builder /build/dist ./web/dist

# Create necessary directories
RUN mkdir -p data scenes/scripts scenes/clips scenes/thumbnails

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "app.main"]
