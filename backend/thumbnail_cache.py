"""Thumbnail caching to disk with persistent storage."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ThumbnailCache:
    """Cache for artwork thumbnails."""

    def __init__(self, cache_dir: str = "/app/data/thumbnails"):
        """
        Initialize thumbnail cache.

        Args:
            cache_dir: Directory to store cached thumbnails
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Thumbnail cache initialized at {self.cache_dir}")

    def get_cache_path(self, content_id: str) -> Path:
        """
        Get cache file path for a content ID.

        Args:
            content_id: Artwork content ID

        Returns:
            Path to cached thumbnail file
        """
        return self.cache_dir / f"{content_id}.jpg"

    def get(self, content_id: str) -> Optional[bytes]:
        """
        Get cached thumbnail if available.

        Args:
            content_id: Artwork content ID

        Returns:
            Cached thumbnail bytes or None if not cached
        """
        cache_file = self.get_cache_path(content_id)
        if cache_file.exists():
            try:
                logger.debug(f"Cache hit for {content_id}")
                return cache_file.read_bytes()
            except Exception as e:
                logger.error(f"Error reading cached thumbnail {content_id}: {e}")
                return None

        logger.debug(f"Cache miss for {content_id}")
        return None

    def set(self, content_id: str, thumbnail_data: bytes) -> None:
        """
        Save thumbnail to cache.

        Args:
            content_id: Artwork content ID
            thumbnail_data: Thumbnail image bytes
        """
        cache_file = self.get_cache_path(content_id)
        try:
            cache_file.write_bytes(thumbnail_data)
            logger.info(f"Cached thumbnail for {content_id} ({len(thumbnail_data)} bytes)")
        except Exception as e:
            logger.error(f"Error caching thumbnail {content_id}: {e}")

    def exists(self, content_id: str) -> bool:
        """
        Check if thumbnail is cached.

        Args:
            content_id: Artwork content ID

        Returns:
            True if cached, False otherwise
        """
        return self.get_cache_path(content_id).exists()

    def delete(self, content_id: str) -> None:
        """
        Delete cached thumbnail.

        Args:
            content_id: Artwork content ID
        """
        cache_file = self.get_cache_path(content_id)
        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.info(f"Deleted cached thumbnail for {content_id}")
            except Exception as e:
                logger.error(f"Error deleting cached thumbnail {content_id}: {e}")

    def clear(self) -> None:
        """Clear all cached thumbnails."""
        try:
            for cache_file in self.cache_dir.glob("*.jpg"):
                cache_file.unlink()
            logger.info("Cleared thumbnail cache")
        except Exception as e:
            logger.error(f"Error clearing thumbnail cache: {e}")


# Global thumbnail cache instance
thumbnail_cache = ThumbnailCache()
