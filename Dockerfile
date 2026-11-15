# Multi-stage build for Samsung Frame Art Controller

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy dependency manifests first so npm ci is cached unless deps change
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend with frontend static files
FROM python:3.11-slim

WORKDIR /app

# Install samsung-tv-ws-api library from a pinned commit (tarball, so no git needed)
# To update: cd samsung-tv-ws-api && git log -1 --format="%H %s"
ARG SAMSUNG_API_COMMIT=d7fc3442c4cdbc4acd3c596fd328792026cee681
RUN pip install --no-cache-dir \
    https://github.com/NickWaterton/samsung-tv-ws-api/archive/${SAMSUNG_API_COMMIT}.tar.gz

# Install Python dependencies before copying code so this layer stays cached
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend files
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "backend/main.py"]
