# Samsung Frame Art Controller

A full-stack web application to manage artwork on your Samsung Frame TV. Control what's displayed, upload new artwork, delete unwanted images, and browse your entire collection from a web interface.

## Architecture

- **Backend**: FastAPI REST API (Python 3.11)
- **Frontend**: Vue 3 with Vite
- **TV Communication**: WebSocket via `samsungtvws` library
- **Deployment**: Single Docker container with multi-stage build
- **Caching**: Two-level caching (in-memory artwork list + persistent disk-based thumbnails)

## Quick Start

See [DOCKER_README.md](DOCKER_README.md) for complete Docker setup instructions.

**TL;DR:**
```bash
# Copy environment template and configure your TV IP
cp .env.example .env
# Edit .env with your TV's IP address

# Build and run
docker-compose up -d

# Access the web interface
open http://localhost:8000
```

## Features

### ✅ View Current Artwork
- See which artwork is currently displayed on your TV
- Green border and ★ star indicator on current artwork
- Real-time updates when artwork changes

### ✅ Browse Art Gallery
- View all artwork available on your TV (uploaded + Art Store + Ambient)
- Filter by type: All, Uploaded Only, or Art Store Only
- Thumbnails for user-uploaded content (DRM prevents Art Store thumbnails)
- Click any thumbnail to select it (displays when TV enters art mode)
- Visual feedback with "Selecting..." overlay during artwork changes

### ✅ Upload New Artwork
- Upload images from your computer
- Choose matte style (shadowbox, modern, etc.) for both landscape and portrait
- Automatic gallery refresh after upload
- Thumbnails automatically cached for future viewing

### ✅ Delete Artwork
- Delete individual artwork with confirmation prompt
- Cannot delete currently displayed artwork (protection)
- Multi-select mode for batch deletion
- Shows success/failure results for each deletion

### ✅ Multi-Select Deletion
- Click "Select Multiple" to enter selection mode
- Check multiple artworks to delete in one operation
- Current artwork is protected and cannot be selected
- Batch delete with detailed success/failure reporting

### ✅ Loading States & Visual Feedback
- "Selecting..." overlay when changing artwork
- Disabled state on other thumbnails during selection
- Prevents accidental double-clicks
- Clear visual feedback for all operations

### ✅ TV Status
- Connection status indicator
- Power state monitoring
- Art mode status
- API version detection

### ✅ Persistent Thumbnail Caching
- Thumbnails stored in Docker volume (`/app/data/thumbnails`)
- Survives container restarts
- Background preloading on startup (fetches all thumbnails)
- Cache automatically cleaned when artwork is deleted

## Content Types

The TV organizes artwork into three types:

- **Uploaded** (`mobile`): Images you've uploaded from your phone or computer
- **Art Store** (`server`/`artstore`): Samsung Art Store purchased/subscribed content
- **Ambient** (`ambient`): Pre-installed ambient mode content

**Note**: Art Store content is DRM-protected and cannot be downloaded. Only user-uploaded artwork has thumbnails available.

## API Endpoints

### TV Status
- `GET /api/health` - Health check and TV connection status
- `GET /api/tv/status` - TV power state and art mode status
- `GET /api/tv/settings` - Brightness and color temperature settings

### Artwork Management
- `GET /api/art/current` - Get currently displayed artwork
- `GET /api/art/list` - List all available artwork (cached, deduplicated)
- `POST /api/art/select` - Select artwork (displays when TV enters art mode)
- `GET /api/art/thumbnail/{id}` - Download artwork thumbnail (cached)
- `POST /api/art/upload` - Upload new artwork with matte selection
- `DELETE /api/art/{id}` - Delete artwork (protected if currently displayed)

### Debug
- `GET /api/art/list/raw` - View raw artwork data from TV API (for debugging)

**API Documentation**: http://localhost:8000/docs (Swagger UI)

## Home Assistant Integration

The REST API can be called directly from Home Assistant to control brightness, color temperature, and artwork selection.

### Brightness Control

Control brightness (0-10) based on time of day or other automations:

```yaml
# configuration.yaml
rest_command:
  samsung_frame_brightness:
    url: "http://YOUR_SERVER_IP:8000/api/art/brightness"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"value": "{{ brightness }}"}'

  samsung_frame_color_temp:
    url: "http://YOUR_SERVER_IP:8000/api/art/color-temperature"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"value": "{{ temp }}"}'
```

### Example Automations

**Dim at sunset:**
```yaml
automation:
  - alias: "Dim Frame TV at Night"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: rest_command.samsung_frame_brightness
        data:
          brightness: "2"

  - alias: "Brighten Frame TV at Sunrise"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: rest_command.samsung_frame_brightness
        data:
          brightness: "7"
```

**Adjust color temperature based on time:**
```yaml
automation:
  - alias: "Warm Frame TV at Night"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: rest_command.samsung_frame_color_temp
        data:
          temp: "5"  # Warmer (removes blue light for nighttime)

  - alias: "Neutral Frame TV During Day"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: rest_command.samsung_frame_color_temp
        data:
          temp: "0"  # Neutral/cooler (more blue light for daytime)
```

### Available REST Endpoints for Home Assistant

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/api/art/brightness` | POST | `{"value": "0-10"}` | Set brightness level |
| `/api/art/color-temperature` | POST | `{"value": "-5 to 5"}` | Set color temperature |
| `/api/art/select` | POST | `{"content_id": "...", "show": false}` | Change artwork |
| `/api/art/list` | GET | - | Get all artwork (for dynamic selection) |
| `/api/tv/status` | GET | - | Get TV status |
| `/api/tv/settings` | GET | - | Get current brightness/color temp |

### Advanced: Dynamic Artwork Selection

You can create automations that change artwork based on conditions:

```yaml
rest_command:
  samsung_frame_select_art:
    url: "http://YOUR_SERVER_IP:8000/api/art/select"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"content_id": "{{ content_id }}", "show": false}'

automation:
  - alias: "Holiday Artwork"
    trigger:
      - platform: time
        at: "00:00:00"
    condition:
      - condition: template
        value_template: "{{ now().month == 12 and now().day >= 1 }}"
    action:
      - service: rest_command.samsung_frame_select_art
        data:
          content_id: "YOUR_HOLIDAY_ARTWORK_ID"
```

**Note:** Replace `YOUR_SERVER_IP` with your Docker host IP address (or hostname). Use port `8000` (or the `API_PORT` you configured).

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Your Samsung Frame TV's IP address
TV_IP=192.168.1.100

# Connection settings
TV_PORT=8001
TV_TIMEOUT=30

# Cache TTL in seconds (artwork list cache)
CACHE_TTL=300

# API server configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## Docker Deployment

The application uses a multi-stage Docker build:

1. **Frontend build stage**: Node 20 Alpine compiles Vue 3 app
2. **Runtime stage**: Python 3.11 slim serves both API and static frontend
3. **Volume**: Persistent thumbnail cache at `/app/data/thumbnails`

```bash
# Build
docker-compose build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Stop and remove volumes (clears thumbnail cache)
docker-compose down -v
```

### Pre-built Images (GitHub Container Registry)

Docker images are automatically built and published via GitHub Actions on every push to `main`:

**Pull the latest image:**
```bash
docker pull ghcr.io/OWNER/REPO:latest
```

**Portainer deployment:**
1. Go to Portainer → Images → Pull Image
2. Enter image name: `ghcr.io/OWNER/REPO:latest`
3. Pull the image
4. Go to Containers → Add Container
5. Use image: `ghcr.io/OWNER/REPO:latest`
6. Configure port mapping: `8000:8000`
7. Add environment variables:
   ```
   TV_IP=192.168.1.100
   TV_PORT=8001
   TV_TIMEOUT=30
   CACHE_TTL=300
   API_HOST=0.0.0.0
   API_PORT=8000
   ```
8. Add volume mapping: `/app/data/thumbnails` → Create new volume
9. Set restart policy to "Always"
10. Deploy container

**Available tags:**
- `latest` - Latest build from main branch
- `main-<sha>` - Specific commit from main branch
- `v1.0.0` - Semantic version tags (if using releases)

**Note:** Replace `OWNER/REPO` with your GitHub username and repository name (e.g., `username/SamsungFrame`).

### GitHub Actions CI/CD

The project includes automated Docker image builds:

**Workflow triggers:**
- Push to `main` → Builds and pushes `latest` tag
- Push tags `v*` → Builds and pushes semantic version tags
- Pull requests → Builds only (does not push)

**Multi-platform builds:**
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64/Apple Silicon)

**View builds:** Go to your GitHub repository → Actions tab

## Local Development (without Docker)

If you want to develop without Docker:

### Backend
```bash
cd backend
pip install -r requirements.txt

# Install samsungtvws from the samsung-tv-ws-api directory
pip install -e ../samsung-tv-ws-api

# Configure .env file
cp ../.env.example .env
# Edit .env with your TV IP

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: http://localhost:8000

### Frontend
```bash
cd frontend
npm install

# Development server with HMR
npm run dev
```

Frontend runs at: http://localhost:5173

The Vite dev server proxies `/api` requests to the backend at `localhost:8000`.

## Project Structure

```
SamsungFrame/
├── .env.example            # Environment template
├── .gitignore             # Git exclusions
├── .dockerignore          # Docker build exclusions
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Docker Compose configuration
├── README.md              # Main README (Docker setup)
├── PROJECT_README.md      # This file (detailed docs)
├── DOCKER_README.md       # Docker-specific setup guide
│
├── .github/
│   └── workflows/
│       └── docker-build.yml  # GitHub Actions CI/CD pipeline
│
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration from .env
│   ├── models.py            # Pydantic request/response models
│   ├── samsung_tv_client.py # Samsung TV API wrapper
│   ├── cache.py             # In-memory artwork list cache
│   ├── thumbnail_cache.py   # Persistent disk-based thumbnail cache
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js       # Vite config with API proxy
│   └── src/
│       ├── main.js          # Vue app entry point
│       ├── App.vue          # Root component
│       ├── api/
│       │   └── samsung-api.js  # Axios-based API client
│       ├── components/
│       │   ├── TvStatus.vue       # Connection status indicator
│       │   ├── CurrentArtwork.vue # Current artwork display
│       │   ├── ArtGallery.vue     # Gallery grid with filtering
│       │   ├── ArtworkCard.vue    # Individual artwork card
│       │   └── UploadForm.vue     # File upload interface
│       └── assets/
│           └── main.css     # Global styles
```

## Caching Strategy

### Artwork List Cache (In-Memory)
- TTL: 5 minutes (configurable via `CACHE_TTL`)
- Invalidated on: Upload, Delete
- Improves performance by reducing TV API calls

### Thumbnail Cache (Persistent Disk)
- Location: Docker volume at `/app/data/thumbnails`
- Format: `{content_id}.jpg`
- Persists across container restarts
- Automatically cleaned when artwork is deleted
- Background preload on startup (fetches all user-uploaded thumbnails)

### Deduplication
- Samsung TV API returns same artwork in multiple categories
- Backend deduplicates by `content_id` before caching
- Prevents duplicate cards in gallery

## Notes & Limitations

### Art Store Content
Samsung Art Store content **cannot be downloaded** due to DRM/licensing restrictions. The API returns thumbnails only for user-uploaded artwork (`mobile` type). Art Store cards show "Art Store" placeholder instead of thumbnails.

### Current Artwork Protection
You cannot delete artwork that's currently being displayed. The UI disables the delete button and shows a ★ indicator. The backend also validates and returns a 400 error if you attempt to delete current artwork.

### Network Requirements
- Backend (Docker container) must reach the TV on the network
- On macOS/Windows, Docker runs in a VM, so `network_mode: host` doesn't work
- Uses standard port mapping: `8000:8000`

### Background Thumbnail Preload
On startup, the backend automatically fetches and caches thumbnails for all user-uploaded artwork. This may take a few seconds depending on how many images you have. Check the Docker logs to see progress:

```bash
docker-compose logs -f | grep "Cached thumbnail"
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Verify .env file exists and has correct TV_IP
cat .env

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Can't connect to TV
- Ensure TV is on the same network as your Docker host
- Verify TV IP address in `.env`
- Check TV is powered on
- Test connection: `ping <TV_IP>`

### Thumbnails not loading
- Art Store content doesn't have thumbnails (DRM protected)
- Check Docker volume exists: `docker volume ls | grep thumbnail`
- Check cache directory: `docker-compose exec samsung-frame-controller ls -la /app/data/thumbnails`
- View logs for thumbnail fetch errors: `docker-compose logs | grep thumbnail`

### Frontend shows blank/white page
- Check backend is running: `curl http://localhost:8000/api/health`
- View browser console for errors (F12)
- Rebuild frontend: `docker-compose build --no-cache`

### Upload fails
- Check file is a valid image format (JPG, PNG, etc.)
- Ensure file isn't too large (TV may have size limits)
- Check backend logs: `docker-compose logs | grep -i error`

## Contributing

When making changes:

1. Test locally with Docker: `docker-compose up --build`
2. Ensure all features work (upload, delete, select, multi-select)
3. Check browser console for errors
4. Update this README if adding new features

### Updating Dependencies

**Samsung TV API Library (`samsung-tv-ws-api`):**

The Dockerfile pins to a specific commit for reproducible builds. To update:

```bash
# Navigate to the local clone
cd /Users/jeff/VSCodeProjects/samsung-tv-ws-api

# Pull latest changes
git pull

# Get the current commit SHA
git log -1 --format="%H %s"

# Copy the commit SHA and update the ARG in Dockerfile:
# ARG SAMSUNG_API_COMMIT=<new-commit-sha>
```

**Why pin to a commit?**
- Ensures reproducible builds across environments
- Prevents unexpected breaking changes from upstream
- Allows controlled testing of library updates
- Makes rollbacks easier if issues arise

## License

This project interfaces with Samsung Frame TVs using the community-maintained `samsungtvws` library. Not affiliated with or endorsed by Samsung.
