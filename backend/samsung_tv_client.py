"""Samsung TV API client wrapper."""

import sys
import logging
from typing import Optional

# Add parent directory to path to access samsung-tv-ws-api
sys.path.append('../samsung-tv-ws-api')

from samsungtvws import SamsungTVWS
from samsungtvws import exceptions as tv_exceptions

from config import settings

logger = logging.getLogger(__name__)


class SamsungTVClient:
    """Wrapper around SamsungTVWS for Frame TV art control."""

    def __init__(self):
        """Initialize the TV client."""
        self._tv: Optional[SamsungTVWS] = None
        self._api_version: Optional[str] = None

    def _get_tv(self) -> SamsungTVWS:
        """Get or create TV connection."""
        if self._tv is None:
            self._tv = SamsungTVWS(
                settings.tv_ip,
                port=settings.tv_port,
                timeout=settings.tv_timeout
            )
        return self._tv

    def is_supported(self) -> bool:
        """Check if art mode is supported on the TV."""
        try:
            tv = self._get_tv()
            return tv.art().supported()
        except Exception as e:
            logger.error(f"Error checking art mode support: {e}")
            return False

    def is_on(self) -> bool:
        """Check if TV is powered on."""
        try:
            tv = self._get_tv()
            return tv.on()
        except Exception as e:
            logger.error(f"Error checking TV power state: {e}")
            return False

    def get_api_version(self) -> Optional[str]:
        """Get the art API version."""
        if self._api_version is None:
            try:
                tv = self._get_tv()
                self._api_version = tv.art().get_api_version()
            except Exception as e:
                logger.error(f"Error getting API version: {e}")
                return None
        return self._api_version

    def get_current_artwork(self) -> dict:
        """Get currently displayed artwork."""
        try:
            tv = self._get_tv()
            return tv.art().get_current()
        except Exception as e:
            logger.error(f"Error getting current artwork: {e}")
            raise

    def get_available_artwork(self) -> list[dict]:
        """Get list of all available artwork, deduplicated by content_id."""
        try:
            tv = self._get_tv()
            artworks = tv.art(10).available()  # 10 second timeout

            # Deduplicate by content_id (same artwork can appear in multiple categories)
            seen_ids = set()
            unique_artworks = []
            for artwork in artworks:
                content_id = artwork.get('content_id')
                if content_id and content_id not in seen_ids:
                    seen_ids.add(content_id)
                    unique_artworks.append(artwork)

            logger.debug(f"Deduplicated {len(artworks)} artworks to {len(unique_artworks)} unique items")
            return unique_artworks
        except Exception as e:
            logger.error(f"Error getting available artwork: {e}")
            raise

    def select_artwork(self, content_id: str, category_id: Optional[str] = None, show: bool = False) -> None:
        """
        Select artwork.

        Args:
            content_id: ID of the artwork to display
            category_id: Optional category ID
            show: If True, force TV into art mode and display immediately.
                  If False, queue artwork for next time TV enters art mode.
        """
        try:
            tv = self._get_tv()
            tv.art().select_image(content_id, category=category_id, show=show)
        except Exception as e:
            logger.error(f"Error selecting artwork {content_id}: {e}")
            raise

    def get_thumbnail(self, content_id: str) -> Optional[bytes]:
        """
        Get thumbnail for artwork.

        Args:
            content_id: ID of the artwork

        Returns:
            JPEG thumbnail bytes or None if unavailable
        """
        try:
            tv = self._get_tv()
            api_version = self.get_api_version()

            if api_version is None:
                logger.warning("Could not determine API version")
                return None

            # Use appropriate method based on API version
            if int(api_version.replace('.', '')) >= 4000:
                logger.debug(f"Using get_thumbnail_list for {content_id}")
                thumbs = tv.art(30).get_thumbnail_list(content_id)
            else:
                logger.debug(f"Using get_thumbnail for {content_id}")
                thumbs = tv.art(30).get_thumbnail(content_id, True)

            if thumbs:
                thumb = list(thumbs.values())[0]
                # Convert bytearray to bytes
                return bytes(thumb) if isinstance(thumb, bytearray) else thumb

            return None

        except tv_exceptions.TimeoutError as e:
            logger.warning(f"Timeout getting thumbnail for {content_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting thumbnail for {content_id}: {e}")
            return None

    def upload_artwork(
        self,
        file_path: str,
        matte: str = "shadowbox_polar",
        portrait_matte: str = "shadowbox_polar"
    ) -> Optional[str]:
        """
        Upload artwork to TV.

        Args:
            file_path: Path to image file
            matte: Matte style for landscape
            portrait_matte: Matte style for portrait

        Returns:
            Content ID of uploaded artwork or None if failed
        """
        try:
            tv = self._get_tv()
            content_id = tv.art(10).upload(file_path, matte=matte, portrait_matte=portrait_matte)
            logger.info(f"Uploaded {file_path} as {content_id}")
            return content_id
        except Exception as e:
            logger.error(f"Error uploading artwork: {e}")
            raise

    def get_artmode_status(self) -> bool:
        """Check if TV is currently in art mode."""
        try:
            tv = self._get_tv()
            status = tv.art().get_artmode()
            return status == "on"
        except Exception as e:
            logger.error(f"Error getting art mode status: {e}")
            return False

    def get_brightness(self) -> Optional[str]:
        """Get current brightness setting."""
        try:
            tv = self._get_tv()
            return tv.art().get_brightness()
        except Exception as e:
            logger.error(f"Error getting brightness: {e}")
            return None

    def get_color_temperature(self) -> Optional[str]:
        """Get current color temperature setting."""
        try:
            tv = self._get_tv()
            return tv.art().get_color_temperature()
        except Exception as e:
            logger.error(f"Error getting color temperature: {e}")
            return None

    def set_brightness(self, value: str) -> None:
        """
        Set brightness level.

        Args:
            value: Brightness level from "0" to "10"
        """
        try:
            tv = self._get_tv()
            tv.art().set_brightness(value)
            logger.info(f"Set brightness to {value}")
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
            raise

    def set_color_temperature(self, value: str) -> None:
        """
        Set color temperature.

        Args:
            value: Color temperature from "-5" to "5"
        """
        try:
            tv = self._get_tv()
            tv.art().set_color_temperature(value)
            logger.info(f"Set color temperature to {value}")
        except Exception as e:
            logger.error(f"Error setting color temperature: {e}")
            raise

    def delete_artwork(self, content_id: str) -> bool:
        """
        Delete artwork from TV.

        Args:
            content_id: ID of the artwork to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            tv = self._get_tv()
            result = tv.art().delete(content_id)
            if result:
                logger.info(f"Deleted artwork: {content_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting artwork {content_id}: {e}")
            raise

    def get_matte_list(self) -> tuple[list[dict], list[dict]]:
        """
        Get available matte types and colors.

        Returns:
            Tuple of (matte_types, matte_colors)
        """
        try:
            tv = self._get_tv()
            matte_types, matte_colors = tv.art().get_matte_list(include_colour=True)
            logger.debug(f"Retrieved {len(matte_types)} matte types and {len(matte_colors)} colors")
            return matte_types, matte_colors
        except Exception as e:
            logger.error(f"Error getting matte list: {e}")
            raise

    def change_matte(self, content_id: str, matte_id: str, portrait_matte_id: Optional[str] = None) -> None:
        """
        Change the matte on artwork.

        Args:
            content_id: ID of the artwork
            matte_id: New matte ID (format: type_color, e.g., "shadowbox_polar")
            portrait_matte_id: Optional portrait matte ID
        """
        try:
            tv = self._get_tv()
            tv.art().change_matte(content_id, matte_id, portrait_matte_id)
            logger.info(f"Changed matte for {content_id} to {matte_id}")
        except Exception as e:
            logger.error(f"Error changing matte for {content_id}: {e}")
            raise


# Global client instance
tv_client = SamsungTVClient()
