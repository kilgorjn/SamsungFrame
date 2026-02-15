# Multi-stage build for Samsung Frame Art Controller

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend with frontend static files
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone and install samsung-tv-ws-api library
# Pinned to specific commit for reproducible builds
# To update: cd samsung-tv-ws-api && git log -1 --format="%H %s"
ARG SAMSUNG_API_COMMIT=d7fc3442c4cdbc4acd3c596fd328792026cee681
RUN git clone https://github.com/NickWaterton/samsung-tv-ws-api.git /app/samsung-tv-ws-api && \
    cd /app/samsung-tv-ws-api && \
    git checkout ${SAMSUNG_API_COMMIT} && \
    cd /app && \
    pip install --no-cache-dir /app/samsung-tv-ws-api

# Copy backend files
COPY backend/ ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "backend/main.py"]
