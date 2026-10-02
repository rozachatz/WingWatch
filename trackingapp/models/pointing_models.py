"""Status of the demo antenna command; separate from the ADS-B report contract."""
from typing import Literal

from pydantic import Field, FiniteFloat

from trackingapp.models.radar_models import RadarModel, Site


class DemoPointingStatus(RadarModel):
    source: Literal['demo_adsb']
    run_id: str
    frame_index: int = Field(ge=0)
    receiver: Site
    selected_hex: str | None
    selected_flight: str | None
    status: Literal['idle', 'commanded', 'no_report']
    command_azimuth_deg: FiniteFloat | None = Field(ge=0, lt=360)
    command_elevation_deg: FiniteFloat | None = Field(ge=0, le=90)
