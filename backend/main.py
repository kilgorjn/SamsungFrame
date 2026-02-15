"""FastAPI application for Samsung Frame Art Controller."""

import logging
import tempfile
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from models import (
    ArtworkInfo,
    ArtworkListResponse,
    CurrentArtworkResponse,
    SelectArtworkRequest,
    TvStatusResponse,
    TvSettingsResponse,
    HealthResponse,
)
from samsung_tv_client import tv_client
from cache import artwork_cache
from thumbnail_cache import thumbnail_cache

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG to see WebSocket events
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Samsung Frame Art Controller API",
    description="REST API for controlling Samsung Frame TV artwork",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def preload_thumbnails():
    """Background task to preload thumbnails for all artwork."""
    try:
        logger.info("Starting thumbnail preload...")
        artworks = tv_client.get_available_artwork()

        # Only download thumbnails for user-uploaded content (not Art Store)
        user_artworks = [art for art in artworks if art.get('content_type') == 'mobile']

        logger.info(f"Found {len(user_artworks)} user-uploaded artworks to cache")

        for i, artwork in enumerate(user_artworks, 1):
            content_id = artwork.get('content_id')
            if not content_id:
                continue

            # Skip if already cached
            if thumbnail_cache.exists(content_id):
                logger.debug(f"[{i}/{len(user_artworks)}] {content_id} already cached")
                continue

            # Download and cache
            try:
                thumbnail_data = tv_client.get_thumbnail(content_id)
                if thumbnail_data:
                    thumbnail_cache.set(content_id, thumbnail_data)
                    logger.info(f"[{i}/{len(user_artworks)}] Cached thumbnail for {content_id}")
            except Exception as e:
                logger.error(f"[{i}/{len(user_artworks)}] Failed to cache {content_id}: {e}")

        logger.info("Thumbnail preload complete")
    except Exception as e:
        logger.error(f"Error during thumbnail preload: {e}")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Samsung Frame Art Controller API")
    logger.info(f"TV IP: {settings.tv_ip}:{settings.tv_port}")

    # Verify TV connection
    if tv_client.is_supported():
        logger.info("✓ Art mode is supported on the TV")

        # Start thumbnail preload in background thread
        preload_thread = threading.Thread(target=preload_thumbnails, daemon=True)
        preload_thread.start()
        logger.info("Started background thumbnail preload")
    else:
        logger.warning("✗ Could not verify art mode support - TV may be unreachable")


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    tv_reachable = tv_client.is_supported()
    return HealthResponse(
        status="healthy" if tv_reachable else "degraded",
        tv_reachable=tv_reachable
    )


@app.get("/api/tv/status", response_model=TvStatusResponse)
async def get_tv_status():
    """Get TV power state and art mode support."""
    try:
        power_on = tv_client.is_on()
        art_supported = tv_client.is_supported()
        art_mode_active = None
        api_version = None

        if power_on and art_supported:
            art_mode_active = tv_client.get_artmode_status()
            api_version = tv_client.get_api_version()

        return TvStatusResponse(
            power_on=power_on,
            art_mode_supported=art_supported,
            art_mode_active=art_mode_active,
            api_version=api_version
        )
    except Exception as e:
        logger.error(f"Error getting TV status: {e}")
        raise HTTPException(status_code=503, detail="TV unreachable")


@app.get("/api/art/current", response_model=CurrentArtworkResponse)
async def get_current_artwork():
    """Get currently displayed artwork."""
    try:
        current = tv_client.get_current_artwork()
        return CurrentArtworkResponse(**current)
    except Exception as e:
        logger.error(f"Error getting current artwork: {e}")
        raise HTTPException(status_code=503, detail="Could not get current artwork")


@app.get("/api/art/list/raw")
async def get_artwork_list_raw():
    """Get raw artwork list from TV (for debugging - includes duplicates)."""
    try:
        tv = tv_client._get_tv()
        raw_artworks = tv.art(10).available()

        return {
            "count": len(raw_artworks),
            "sample": raw_artworks[:5] if len(raw_artworks) > 5 else raw_artworks,
            "all_artworks": raw_artworks
        }
    except Exception as e:
        logger.error(f"Error getting raw artwork list: {e}")
        raise HTTPException(status_code=503, detail="Could not get raw artwork list")


@app.get("/api/art/list", response_model=ArtworkListResponse)
async def get_artwork_list():
    """Get list of all available artwork (cached and deduplicated)."""
    # Check cache first
    cached = artwork_cache.get("artwork_list")
    if cached is not None:
        logger.debug("Returning cached artwork list")
        return cached

    try:
        artworks = tv_client.get_available_artwork()

        # Convert to ArtworkInfo models
        artwork_list = [ArtworkInfo(**art) for art in artworks]

        response = ArtworkListResponse(
            count=len(artwork_list),
            artworks=artwork_list
        )

        # Cache the response
        artwork_cache.set("artwork_list", response)

        return response
    except Exception as e:
        logger.error(f"Error getting artwork list: {e}")
        raise HTTPException(status_code=503, detail="Could not get artwork list")


@app.post("/api/art/select")
async def select_artwork(request: SelectArtworkRequest):
    """Change displayed artwork."""
    try:
        tv_client.select_artwork(request.content_id, request.category_id)
        return {"success": True, "content_id": request.content_id}
    except Exception as e:
        logger.error(f"Error selecting artwork: {e}")
        raise HTTPException(status_code=500, detail="Could not select artwork")


@app.get("/api/art/thumbnail/{content_id}")
async def get_thumbnail(content_id: str):
    """
    Download artwork thumbnail.

    Returns JPEG image bytes. Thumbnails are cached for performance.
    Note: Art Store content may not be downloadable.
    """
    try:
        # Check cache first
        cached_thumbnail = thumbnail_cache.get(content_id)
        if cached_thumbnail:
            logger.debug(f"Serving cached thumbnail for {content_id}")
            return Response(
                content=cached_thumbnail,
                media_type="image/jpeg",
                headers={"Content-Disposition": f"attachment; filename={content_id}.jpg"}
            )

        # Download from TV if not cached
        thumbnail_data = tv_client.get_thumbnail(content_id)

        if thumbnail_data is None:
            raise HTTPException(
                status_code=404,
                detail="Thumbnail not available (Art Store content cannot be downloaded)"
            )

        # Save to cache
        thumbnail_cache.set(content_id, thumbnail_data)

        return Response(
            content=thumbnail_data,
            media_type="image/jpeg",
            headers={"Content-Disposition": f"attachment; filename={content_id}.jpg"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
        raise HTTPException(status_code=500, detail="Could not get thumbnail")


@app.post("/api/art/upload")
async def upload_artwork(
    file: UploadFile = File(...),
    matte: str = Form("shadowbox_polar"),
    portrait_matte: str = Form("shadowbox_polar")
):
    """Upload new artwork to TV."""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Upload to TV
            content_id = tv_client.upload_artwork(tmp_path, matte, portrait_matte)

            if content_id is None:
                raise HTTPException(status_code=500, detail="Upload failed")

            # Invalidate artwork list cache
            artwork_cache.invalidate("artwork_list")

            return {
                "success": True,
                "content_id": content_id,
                "filename": file.filename
            }

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading artwork: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.delete("/api/art/{content_id}")
async def delete_artwork(content_id: str):
    """
    Delete artwork from TV.

    Cannot delete currently displayed artwork.
    """
    try:
        # Check if this is the currently displayed artwork
        # (gracefully handle if we can't get current artwork due to WebSocket issues)
        try:
            current = tv_client.get_current_artwork()
            if current.get("content_id") == content_id:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete currently displayed artwork. Please select a different artwork first."
                )
        except HTTPException:
            raise  # Re-raise the 400 error if it's the current artwork
        except Exception as e:
            # If we can't check current artwork (e.g., WebSocket disconnect), log and continue
            logger.warning(f"Could not verify current artwork before deletion (will proceed): {e}")

        result = tv_client.delete_artwork(content_id)

        if result:
            # Invalidate caches
            artwork_cache.invalidate("artwork_list")
            thumbnail_cache.delete(content_id)

            return {
                "success": True,
                "content_id": content_id,
                "message": "Artwork deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Delete operation failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting artwork: {e}")
        raise HTTPException(status_code=500, detail=f"Could not delete artwork: {str(e)}")


@app.get("/api/tv/settings", response_model=TvSettingsResponse)
async def get_tv_settings():
    """Get TV art mode settings (brightness, color temperature)."""
    try:
        brightness = tv_client.get_brightness()
        color_temp = tv_client.get_color_temperature()

        return TvSettingsResponse(
            brightness=brightness,
            color_temperature=color_temp
        )
    except Exception as e:
        logger.error(f"Error getting TV settings: {e}")
        raise HTTPException(status_code=503, detail="Could not get TV settings")


# Mount static files for frontend (if available)
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "dist"
if STATIC_DIR.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    # Catch-all route for Vue.js SPA (must be last)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the Vue.js SPA for all non-API routes."""
        # If path doesn't start with /api, serve index.html
        if not full_path.startswith("api"):
            index_file = STATIC_DIR / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not found")
else:
    logger.warning("Frontend dist directory not found. API-only mode.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
