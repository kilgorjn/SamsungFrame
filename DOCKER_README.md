# Samsung Frame Art Controller - Docker Setup

Run the entire application (backend + frontend) in a single Docker container.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at **http://localhost:8000**

### Using Docker CLI

```bash
# Build the image
docker build -t samsung-frame-controller .

# Run the container
docker run -d \
  --name samsung-frame-controller \
  --network host \
  -e TV_IP=192.168.86.25 \
  samsung-frame-controller

# View logs
docker logs -f samsung-frame-controller

# Stop the container
docker stop samsung-frame-controller
docker rm samsung-frame-controller
```

## Configuration

### Environment Variables

You can customize the following environment variables:

```yaml
TV_IP: 192.168.86.25          # Your Samsung TV IP address
TV_PORT: 8001                 # Samsung TV port (default: 8001)
TV_TIMEOUT: 30                # Connection timeout in seconds
CACHE_TTL: 300                # Cache TTL in seconds (5 minutes)
API_HOST: 0.0.0.0             # API host
API_PORT: 8000                # API port
```

### Edit docker-compose.yml

```yaml
environment:
  - TV_IP=192.168.86.25  # Change to your TV's IP
  - TV_PORT=8001
  - TV_TIMEOUT=30
```

Or create a `.env` file in the project root:

```bash
TV_IP=192.168.86.25
TV_PORT=8001
TV_TIMEOUT=30
CACHE_TTL=300
```

## How It Works

The Docker image uses a multi-stage build:

1. **Stage 1**: Build Vue.js frontend
   - Uses Node.js to build static files
   - Output: `frontend/dist/`

2. **Stage 2**: Python backend + static frontend
   - Installs Python dependencies
   - Clones `samsung-tv-ws-api` library
   - Copies built frontend files
   - Serves frontend via FastAPI

## Network Mode

The container uses `network_mode: host` to access your TV on the local network. This means:
- ✅ The container can communicate with devices on your LAN
- ✅ No port mapping complexity
- ⚠️ The container shares the host's network stack

If you prefer bridge networking:

```yaml
services:
  samsung-frame-controller:
    # Remove network_mode: host
    ports:
      - "8000:8000"
    environment:
      - TV_IP=192.168.86.25  # Must be accessible from container
```

## Usage

Once the container is running:

1. **Open your browser**: http://localhost:8000
2. **View TV status**: See connection and power state
3. **Browse artwork**: See all available art on your TV
4. **Select artwork**: Click any artwork card to display it
5. **Upload new art**: Use the upload form to add images
6. **Download thumbnails**: Available for uploaded content

## API Documentation

Swagger UI is available at: http://localhost:8000/docs

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Can't connect to TV
```bash
# Verify TV IP is correct
docker-compose exec samsung-frame-controller ping <TV_IP>

# Check environment variables
docker-compose exec samsung-frame-controller env | grep TV
```

### Frontend not loading
```bash
# Verify frontend was built
docker-compose exec samsung-frame-controller ls -la /app/frontend/dist

# Check logs for errors
docker-compose logs | grep ERROR
```

## Development vs Production

### Development (separate services)
```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

### Production (single container)
```bash
# Docker container
docker-compose up -d
```

## Building for Different Architectures

```bash
# For ARM (Raspberry Pi, Apple Silicon)
docker buildx build --platform linux/arm64 -t samsung-frame-controller .

# For AMD64 (Most PCs)
docker buildx build --platform linux/amd64 -t samsung-frame-controller .

# Multi-platform
docker buildx build --platform linux/amd64,linux/arm64 -t samsung-frame-controller .
```

## Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# View only recent logs
docker-compose logs --tail=100

# Enter container shell
docker-compose exec samsung-frame-controller /bin/sh
```

## Resource Usage

The container is lightweight:
- Image size: ~500-700 MB
- Memory: ~100-200 MB
- CPU: Minimal (idle), spikes during thumbnail downloads/uploads

## Security Notes

- The application communicates with your TV over WebSocket (port 8001)
- No authentication is implemented - use on trusted networks only
- Consider adding nginx reverse proxy with HTTPS for production
- The TV's art API does not require authentication

## Alternative: Docker Hub

To publish to Docker Hub:

```bash
# Build
docker build -t yourusername/samsung-frame-controller .

# Push
docker push yourusername/samsung-frame-controller

# Run from Docker Hub
docker run -d --network host yourusername/samsung-frame-controller
```
