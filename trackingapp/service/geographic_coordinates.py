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


def pointing_angles(receiver: Site, target: Site) -> tuple[float, float]:
    """WGS84 line-of-sight azimuth/elevation in degrees from receiver to target."""
    latitude, longitude = math.radians(receiver.latitude), math.radians(receiver.longitude)
    dx, dy, dz = (target_coord - site_coord for target_coord, site_coord
                  in zip(ecef(target), ecef(receiver)))
    east = -math.sin(longitude) * dx + math.cos(longitude) * dy
    north = (-math.sin(latitude) * math.cos(longitude) * dx
             - math.sin(latitude) * math.sin(longitude) * dy
             + math.cos(latitude) * dz)
    up = (math.cos(latitude) * math.cos(longitude) * dx
          + math.cos(latitude) * math.sin(longitude) * dy
          + math.sin(latitude) * dz)
    azimuth = math.degrees(math.atan2(east, north)) % 360
    elevation = math.degrees(math.atan2(up, math.hypot(east, north)))
    return azimuth, max(0.0, min(elevation, 90.0))
