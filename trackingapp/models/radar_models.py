"""RadarFrame v2 models matching Malaxa's handoff contract."""
from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, FiniteFloat, field_validator


class RadarModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Site(RadarModel):
    name: str
    latitude: FiniteFloat = Field(ge=-90, le=90)
    longitude: FiniteFloat = Field(ge=-180, le=180)
    altitude_m: FiniteFloat


class Position(RadarModel):
    latitude: FiniteFloat = Field(ge=-90, le=90)
    longitude: FiniteFloat = Field(ge=-180, le=180)
    altitude_m: FiniteFloat | None
    position_source: Literal["azimuth", "multistatic", "constrained", "demo"]


class Localization(RadarModel):
    available: bool
    method: Literal["none", "azimuth", "multistatic", "constrained", "demo"]
    note: str


class RadarTarget(RadarModel):
    track_id: int = Field(ge=1)
    status: Literal["tentative", "confirmed", "coasting"]
    bistatic_range_m: FiniteFloat
    excess_range_m: FiniteFloat
    range_rate_mps: FiniteFloat
    doppler_hz: FiniteFloat
    confidence: FiniteFloat | None = Field(ge=0, le=1)
    age_frames: int = Field(ge=1)
    misses: int = Field(ge=0)
    position: Position | None


class RadarFrame(RadarModel):
    schema_version: Literal[2]
    run_id: str
    mode: Literal["replay", "live"]
    frame_index: int = Field(ge=0)
    timestamp: datetime
    frequency_mhz: FiniteFloat
    receiver: Site
    transmitter: Site
    localization: Localization
    targets: list[RadarTarget]
    range_doppler_image_url: str | None = None

    @field_validator("timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value


class RadarStatus(RadarModel):
    source: Literal["files"]
    service_status: Literal["ok", "error"]
    mode: Literal["replay", "live"]
    run_id: str | None
    latest_frame_index: int | None = Field(ge=0)
    last_update_utc: AwareDatetime | None
    source_connected: bool
    paused: bool
    error: str | None
