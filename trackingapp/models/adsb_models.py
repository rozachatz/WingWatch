"""Separate ADS-B replay data; altitude is metres above the WGS84 ellipsoid."""
from typing import Literal

from pydantic import AwareDatetime, Field, FiniteFloat

from trackingapp.models.radar_models import RadarModel


class AdsbAircraft(RadarModel):
    hex: str = Field(pattern=r'^[0-9a-fA-F]{6}$')
    flight: str
    lat: FiniteFloat = Field(ge=-90, le=90)
    lon: FiniteFloat = Field(ge=-180, le=180)
    altitude: FiniteFloat
    altitude_datum: Literal['WGS84 ellipsoid']
    timestamp: AwareDatetime
    source: Literal['demo_adsb']


class AdsbFrame(RadarModel):
    frame_index: int = Field(ge=1)
    timestamp: AwareDatetime
    aircraft: list[AdsbAircraft]


class AdsbReplay(RadarModel):
    schema_version: Literal[1]
    frames: list[AdsbFrame]
