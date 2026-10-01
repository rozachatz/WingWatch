"""WGS84 coordinate helper shared by fixture generation and contours."""
import math

from trackingapp.models.radar_models import Site


def ecef(site: Site) -> tuple[float, float, float]:
    """WGS84 ECEF coordinates; site heights are ellipsoidal metres."""
    lat, lon = math.radians(site.latitude), math.radians(site.longitude)
    eccentricity_squared = 6.69437999014e-3
    radius = 6_378_137.0 / math.sqrt(1 - eccentricity_squared * math.sin(lat) ** 2)
    return ((radius + site.altitude_m) * math.cos(lat) * math.cos(lon),
            (radius + site.altitude_m) * math.cos(lat) * math.sin(lon),
            (radius * (1 - eccentricity_squared) + site.altitude_m) * math.sin(lat))
