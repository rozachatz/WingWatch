"""Constant-altitude bistatic range contour for the local demo geometry."""
import math

from trackingapp.models.radar_models import Site
from trackingapp.service.geographic_coordinates import ecef

ASSUMED_ALTITUDE_M = 1_000.0


def range_contour(receiver: Site, transmitter: Site, range_m: float, bearing_offset_rad: float = 0.0) -> list[list[float]]:
    """Return a closed GeoJSON ring at 1,000 m WGS84 ellipsoidal height.

    Numerically solves Tx-to-point + point-to-Rx in ECEF coordinates along
    radial directions around the sites' midpoint. This is an ellipse-like
    surface contour, not an estimated aircraft location. Restricted to local
    geometry with the midpoint inside the contour; no global localization.
    """
    if not math.isfinite(bearing_offset_rad):
        raise ValueError("bearing offset must be finite")
    if not math.isfinite(range_m) or not 0 < range_m <= 100_000:
        raise ValueError("demo contour range must be finite and between 0 and 100 km")
    if abs(receiver.longitude - transmitter.longitude) > 180:
        raise ValueError("demo contour does not support sites across the date line")
    rx, tx = ecef(receiver), ecef(transmitter)
    if math.dist(rx, tx) > 100_000:
        raise ValueError("demo sites must be within 100 km of each other")
    lat0 = math.radians((receiver.latitude + transmitter.latitude) / 2)
    lon0 = math.radians((receiver.longitude + transmitter.longitude) / 2)

    def point(distance: float, bearing: float) -> Site:
        angle = distance / 6_371_000.0
        lat = math.asin(math.sin(lat0) * math.cos(angle)
                        + math.cos(lat0) * math.sin(angle) * math.cos(bearing))
        lon = lon0 + math.atan2(math.sin(bearing) * math.sin(angle) * math.cos(lat0),
                               math.cos(angle) - math.sin(lat0) * math.sin(lat))
        return Site(name="Contour point", latitude=math.degrees(lat),
                    longitude=(math.degrees(lon) + 180) % 360 - 180,
                    altitude_m=ASSUMED_ALTITUDE_M)

    def path_length(distance: float, bearing: float) -> float:
        xyz = ecef(point(distance, bearing))
        return math.dist(tx, xyz) + math.dist(rx, xyz)

    if path_length(0, 0) >= range_m:
        raise ValueError("range is too small for this demo altitude and midpoint solver")
    ring = []
    for index in range(96):
        bearing = bearing_offset_rad + index * 2 * math.pi / 96
        low, high = 0.0, range_m
        if path_length(high, bearing) < range_m:
            raise ValueError("could not bracket the range contour")
        for _ in range(32):
            middle = (low + high) / 2
            if path_length(middle, bearing) < range_m:
                low = middle
            else:
                high = middle
        site = point((low + high) / 2, bearing)
        ring.append([site.longitude, site.latitude])
    ring.append(ring[0].copy())
    return ring
