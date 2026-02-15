# Samsung Frame Art Controller

Web application to control and manage artwork on your Samsung Frame TV.

## Features

- 🖼️ **View Current Artwork** - See what's currently displayed
- 🎨 **Browse Art Gallery** - View all available artwork
- 🔄 **Change Artwork** - Select and display different art with one click
- ⬆️ **Upload Images** - Add your own artwork to the TV
- 📥 **Download Thumbnails** - Save thumbnails of uploaded art
- ⚙️ **TV Settings** - View brightness and color temperature

## Quick Start with Docker (Recommended)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd SamsungFrame

# 2. Configure your TV IP (optional, defaults to 192.168.86.25)
cp .env.example .env
# Edit .env and set TV_IP to your TV's IP address

# 3. Run with Docker Compose
docker-compose up -d

# 4. Open in browser
open http://localhost:8000
```

That's it! The application is now running at http://localhost:8000

## Alternative: Development Setup

For development or if you prefer running without Docker:

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

## Documentation

- **Docker Setup**: [DOCKER_README.md](DOCKER_README.md) - Complete Docker guide
- **Development**: [PROJECT_README.md](PROJECT_README.md) - Development setup
- **API Docs**: http://localhost:8000/docs (when running)

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vue 3 + Vite
- **TV API**: [samsung-tv-ws-api](https://github.com/NickWaterton/samsung-tv-ws-api)
- **Deployment**: Docker + Docker Compose

## Requirements

- Docker & Docker Compose (for Docker deployment)
- OR Python 3.9+ & Node.js 18+ (for development)
- Samsung Frame TV on the same network

## Architecture

```
┌─────────────┐
│  Browser    │
│ (port 8000) │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Docker Container   │
│  ┌───────────────┐  │
│  │  FastAPI      │  │
│  │  Backend      │  │
│  │  + Vue SPA    │  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │
           ▼
    ┌─────────────┐
    │  Samsung    │
    │  Frame TV   │
    └─────────────┘
```

## License

MIT

## Credits

Uses the excellent [samsung-tv-ws-api](https://github.com/NickWaterton/samsung-tv-ws-api) by NickWaterton.