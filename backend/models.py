"""Pydantic models for API requests and responses."""

from typing import Optional
from pydantic import BaseModel


class ArtworkInfo(BaseModel):
    """Model for artwork metadata."""

    content_id: str
    content_type: str
    category_id: Optional[str] = None
    file_name: Optional[str] = None
    matte_id: Optional[str] = None
    portrait_matte_id: Optional[str] = None


class ArtworkListResponse(BaseModel):
    """Model for list of artworks."""

    count: int
    artworks: list[ArtworkInfo]


class CurrentArtworkResponse(BaseModel):
    """Model for current artwork response."""

    content_id: str
    content_type: str
    matte_id: Optional[str] = None
    portrait_matte_id: Optional[str] = None
    category_id: Optional[str] = None


class SelectArtworkRequest(BaseModel):
    """Model for selecting artwork."""

    content_id: str
    category_id: Optional[str] = None


class UploadArtworkRequest(BaseModel):
    """Model for upload artwork metadata (file sent separately)."""

    matte: str = "shadowbox_polar"
    portrait_matte: str = "shadowbox_polar"


class TvStatusResponse(BaseModel):
    """Model for TV status."""

    power_on: bool
    art_mode_supported: bool
    art_mode_active: Optional[bool] = None
    api_version: Optional[str] = None


class TvSettingsResponse(BaseModel):
    """Model for TV settings."""

    brightness: Optional[str] = None
    color_temperature: Optional[str] = None


class HealthResponse(BaseModel):
    """Model for health check response."""

    status: str
    tv_reachable: bool
