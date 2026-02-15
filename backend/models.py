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
    width: Optional[int] = None
    height: Optional[int] = None
    image_date: Optional[str] = None


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
    show: bool = False  # If True, force TV into art mode and display immediately


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


class MatteType(BaseModel):
    """Model for matte type."""

    matte_type: str


class MatteColor(BaseModel):
    """Model for matte color."""

    color: str
    R: int
    G: int
    B: int


class MatteListResponse(BaseModel):
    """Model for available mattes response."""

    matte_types: list[MatteType]
    matte_colors: list[MatteColor]


class ChangeMatteRequest(BaseModel):
    """Model for change matte request."""

    content_id: str
    matte_id: str
    portrait_matte_id: Optional[str] = None


class SetBrightnessRequest(BaseModel):
    """Model for set brightness request."""

    value: str  # "0" to "10"


class SetColorTemperatureRequest(BaseModel):
    """Model for set color temperature request."""

    value: str  # "-5" to "5"


class HealthResponse(BaseModel):
    """Model for health check response."""

    status: str
    tv_reachable: bool
