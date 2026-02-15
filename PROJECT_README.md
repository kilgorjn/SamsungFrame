# Samsung Frame Art Controller - Setup Guide

A full-stack web application to manage artwork on your Samsung Frame TV.

## Architecture

- **Backend**: FastAPI REST API (Python)
- **Frontend**: Vue 3 with Vite
- **TV Communication**: WebSocket via `samsungtvws` library

## Prerequisites

- Python 3.9+
- Node.js 18+
- Samsung Frame TV on the same network

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Install dependencies (make sure samsungtvws is available from ../samsung-tv-ws-api)
pip install -r requirements.txt

# Configure environment (edit .env if needed)
# TV_IP is already set to 192.168.86.25

# Start the backend server
python main.py
```

The backend will start on `http://localhost:8000`

**Swagger API Documentation**: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:5173`

## Features

### ✅ View Current Artwork
- See which artwork is currently displayed on your TV
- View thumbnail (for uploaded content)
- See metadata (matte style, type, etc.)

### ✅ Browse Art Gallery
- View all artwork available on your TV
- Filter by type (Uploaded vs Art Store)
- Thumbnails for user-uploaded content
- Click to select and display artwork

### ✅ Upload New Artwork
- Upload images from your computer
- Choose matte style (shadowbox, modern, etc.)
- Automatic refresh of gallery after upload

### ✅ TV Status
- Connection status
- Power state
- Art mode status
- API version

## API Endpoints

### TV Status
- `GET /api/health` - Health check
- `GET /api/tv/status` - TV power and art mode status
- `GET /api/tv/settings` - Brightness and color temperature

### Artwork Management
- `GET /api/art/current` - Get current artwork
- `GET /api/art/list` - List all artwork (cached)
- `POST /api/art/select` - Change displayed artwork
- `GET /api/art/thumbnail/{id}` - Download thumbnail
- `POST /api/art/upload` - Upload new artwork

## Notes

### Art Store Content
Samsung Art Store content **cannot be downloaded** due to DRM/licensing restrictions. Thumbnails are only available for user-uploaded artwork.

### Caching
The artwork list is cached for 5 minutes to improve performance. The cache is automatically invalidated when new artwork is uploaded.

### Network
Both the backend server and your browser must be able to reach the Samsung TV on the network.

## Troubleshooting

### Backend won't start
- Check that `samsungtvws` is installed
- Verify the path to `samsung-tv-ws-api` in `samsung_tv_client.py` line 8
- Check `.env` file has correct TV IP address

### Can't connect to TV
- Ensure TV is on the same network
- Verify TV IP address in `.env`
- Check TV is powered on

### Frontend can't reach backend
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify Vite proxy configuration

### Upload fails
- Check file is a valid image format
- Ensure file isn't too large
- Check backend logs for errors

## Development

### Backend
```bash
cd backend
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
# Development server with HMR
npm run dev

# Build for production
npm run build
```

## Project Structure

```
SamsungFrame/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── samsung_tv_client.py # TV API wrapper
│   ├── cache.py             # Caching logic
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment config
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Main component
│   │   ├── main.js          # Entry point
│   │   ├── api/
│   │   │   └── samsung-api.js  # API client
│   │   ├── components/
│   │   │   ├── TvStatus.vue
│   │   │   ├── CurrentArtwork.vue
│   │   │   ├── ArtGallery.vue
│   │   │   ├── ArtworkCard.vue
│   │   │   └── UploadForm.vue
│   │   └── assets/
│   │       └── main.css     # Styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── frame-test1.py          # Original test script
```
