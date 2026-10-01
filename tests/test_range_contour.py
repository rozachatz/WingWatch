import math
from datetime import datetime, timezone

from fastapi.testclient import TestClient
import pytest

from trackingapp.main import create_app
from trackingapp.models.radar_models import Site
from trackingapp.service.radar_service import RadarService
from trackingapp.demo_fixture_generator import RECEIVER, TRANSMITTER, ecef, make_frame
from trackingapp.service.range_contour_service import ASSUMED_ALTITUDE_M, range_contour


def test_contour_points_satisfy_bistatic_range_at_assumed_altitude():
    for total_range in (12_500, 11_800):
        ring = range_contour(RECEIVER, TRANSMITTER, total_range)
        assert len(ring) == 97 and ring[0] == ring[-1]
        for lon, lat in ring:
            xyz = ecef(Site(name='test', latitude=lat, longitude=lon, altitude_m=ASSUMED_ALTITUDE_M))
            length = math.dist(xyz, ecef(RECEIVER)) + math.dist(xyz, ecef(TRANSMITTER))
            assert length == pytest.approx(total_range, abs=0.001)
    large = range_contour(RECEIVER, TRANSMITTER, 12_500)
    small = range_contour(RECEIVER, TRANSMITTER, 11_800)
    assert max(p[0] for p in small) < max(p[0] for p in large)
    assert min(p[0] for p in small) > min(p[0] for p in large)


@pytest.mark.parametrize('range_m', [100, float('nan'), float('inf'), 100_001])
def test_impossible_or_unsupported_range_is_rejected(range_m):
    with pytest.raises(ValueError):
        range_contour(RECEIVER, TRANSMITTER, range_m)


def test_contour_endpoint_checks_snapshot_identity_and_track_presence():
    service = RadarService(interval_seconds=3600)
    with TestClient(create_app('demo', service)) as client:
        service.latest = make_frame(4, service.run_id, datetime.now(timezone.utc))
        query = {'run_id': service.run_id, 'frame_index': 4}
        response = client.get('/api/v1/tracks/1/contour', params=query)
        assert response.status_code == 200
        contour = response.json()
        assert contour['geometry']['type'] == 'Polygon'
        assert contour['properties']['assumed_altitude_m'] == 1000
        assert contour['properties']['position_estimate'] is False
        assert client.get('/api/v1/tracks/2/contour', params=query).status_code == 404
        assert client.get('/api/v1/tracks/1/contour', params={**query, 'frame_index': 3}).status_code == 409
        assert client.get('/api/v1/tracks/1/contour', params={**query, 'run_id': 'old-run'}).status_code == 409
