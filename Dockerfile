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
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    cython3 \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# ARG is needed to use TARGETARCH
ARG TARGETARCH

# Install dependencies
# If we are on amd64 (Server/PC), we KEEP the emulator for testing.
# If we are on arm64 (Raspberry Pi), we REMOVE it to save space and avoid conflicts.
RUN if [ "$TARGETARCH" = "arm64" ]; then \
        sed -i '/RGBMatrixEmulator/d' requirements.txt; \
    fi && \
    pip install --no-cache-dir "Pillow==10.4.0" -r requirements.txt

# Download Pillow source to get Imaging.h, then build matrix library
RUN pip download --no-binary=Pillow --dest . "Pillow==10.4.0" \
    && mkdir pillow-src \
    && tar -xzf pillow-*.tar.gz -C pillow-src --strip-components=1 \
    && export C_INCLUDE_PATH=/app/pillow-src/src/libImaging \
    && git clone https://github.com/hzeller/rpi-rgb-led-matrix.git /opt/rpi-rgb-led-matrix \
    && cd /opt/rpi-rgb-led-matrix/bindings/python \
    && make build-python PYTHON=$(which python3) \
    && make install-python PYTHON=$(which python3) \
    && rm -rf /app/pillow*

# Create necessary directories first
RUN mkdir -p data scenes/scripts scenes/clips scenes/thumbnails

# Copy application code
COPY app/ ./app/
# Copy scenes to working dir AND a backup location for volume restoration
COPY scenes/ ./scenes/
COPY scenes/ /app/defaults/scenes/

COPY emulator_config.json ./
COPY VERSION ./

# Copy and setup entrypoint
COPY entrypoint.sh /app/entrypoint.sh
# Fix Windows line endings in entrypoint.sh (just in case) using sed, then make executable
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Copy built frontend from stage 1
COPY --from=frontend-builder /build/dist ./web/dist

# Expose port
EXPOSE 8000

# Set Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the application
CMD ["python", "-m", "app.main"]
