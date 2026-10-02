"""Demo pointing follows ADS-B reports, independently of radar-track status."""
import asyncio
import math

from fastapi.testclient import TestClient
import pytest

from trackingapp.main import create_app
from trackingapp.models.radar_models import Site
from trackingapp.service.geographic_coordinates import pointing_angles
from trackingapp.service.radar_service import RadarService


def test_shared_pointing_geometry_has_expected_bearing():
    receiver = Site(name='receiver', latitude=0, longitude=0, altitude_m=0)
    east = Site(name='east', latitude=0, longitude=0.01, altitude_m=100)
    azimuth, elevation = pointing_angles(receiver, east)
    assert azimuth == pytest.approx(90, abs=0.01)
    assert 0 < elevation < 90


def test_demo_selection_updates_command_and_restart_clears_it():
    service = RadarService(interval_seconds=3600)
    with TestClient(create_app('demo', service)) as client:
        first = client.get('/api/v1/frames/latest').json()
        params = {'run_id': first['run_id'], 'frame_index': first['frame_index']}
        idle = client.get('/api/v1/pointing', params=params).json()
        assert idle['status'] == 'idle' and idle['command_azimuth_deg'] is None
        assert client.post('/api/select_aircraft/abc001').status_code == 200
        selected = client.get('/api/v1/pointing', params=params).json()
        assert selected['status'] == 'commanded' and selected['selected_flight'] == 'DEMO01'
        assert math.isfinite(selected['command_azimuth_deg'])
        assert math.isfinite(selected['command_elevation_deg'])

        # Advance through a coasting frame while the radar replay task is parked.
        service.latest = service.frames[6].model_copy(update={'run_id': first['run_id']})
        asyncio.run(service.demo_pointing.advance(service.latest, service.current_aircraft()))
        later_params = {'run_id': first['run_id'], 'frame_index': 7}
        moved = client.get('/api/v1/pointing', params=later_params).json()
        assert moved['status'] == 'commanded'
        assert moved['command_azimuth_deg'] != pytest.approx(selected['command_azimuth_deg'])
        assert client.get('/api/v1/pointing', params=params).status_code == 409

        # ADS-B pointing continues after the radar track is removed.
        service.latest = service.frames[9].model_copy(update={'run_id': first['run_id']})
        asyncio.run(service.demo_pointing.advance(service.latest, service.current_aircraft()))
        removed = client.get('/api/v1/pointing', params={'run_id': first['run_id'],
                             'frame_index': 10}).json()
        assert not service.latest.targets and removed['status'] == 'commanded'

        restarted = client.post('/api/v1/replay/restart').json()
        assert restarted['run_id'] != first['run_id']
        assert client.get('/api/v1/pointing', params={'run_id': restarted['run_id'],
                   'frame_index': restarted['frame_index']}).json()['status'] == 'idle'
        assert client.get('/api/v1/pointing', params=later_params).status_code == 409


def test_demo_rejects_aircraft_missing_from_current_report():
    service = RadarService(interval_seconds=3600)
    with TestClient(create_app('demo', service)) as client:
        assert client.post('/api/select_aircraft/unknown').status_code == 404


def test_hardware_aircraft_selection_route_still_delegates():
    from unittest.mock import Mock

    app = create_app('demo', RadarService(interval_seconds=3600))
    with TestClient(app) as client:
        hardware = Mock()
        hardware.select_airplane.return_value = 'Tracking airplane abc001'
        app.state.track_service = hardware
        assert client.post('/api/select_aircraft/abc001').json() == 'Tracking airplane abc001'
        hardware.select_airplane.assert_called_once_with('abc001')
        frame = client.get('/api/v1/frames/latest').json()
        assert client.get('/api/v1/pointing', params={
            'run_id': frame['run_id'], 'frame_index': frame['frame_index']}).status_code == 409


def test_demo_calls_rotator_service_and_records_commands(monkeypatch):
    from trackingapp.service.rotator_configure_service import RotatorConfigureService

    calls = []
    actual_execute = RotatorConfigureService.execute_async

    async def observe(service, *, latitude, longitude, altitude_m):
        calls.append((latitude, longitude, altitude_m))
        return await actual_execute(
            service, latitude=latitude, longitude=longitude, altitude_m=altitude_m)

    monkeypatch.setattr(RotatorConfigureService, 'execute_async', observe)
    replay = RadarService(interval_seconds=3600)
    with TestClient(create_app('demo', replay)) as client:
        assert calls == []
        report = replay.current_aircraft()[0]
        client.post('/api/select_aircraft/abc001').raise_for_status()
        assert calls == [(report.lat, report.lon, report.altitude)]
        command = replay.demo_pointing.rotator_client.last_command
        frame = client.get('/api/v1/frames/latest').json()
        status = client.get('/api/v1/pointing', params={
            'run_id': frame['run_id'], 'frame_index': frame['frame_index']}).json()
        assert command == (status['command_azimuth_deg'], status['command_elevation_deg'])

        replay.latest = replay.frames[6].model_copy(update={'run_id': frame['run_id']})
        next_report = replay.current_aircraft()[0]
        asyncio.run(replay.demo_pointing.advance(replay.latest, replay.current_aircraft()))
        assert calls[-1] == (next_report.lat, next_report.lon, next_report.altitude)
        assert len(replay.demo_pointing.rotator_client.commands) == 2
        assert replay.demo_pointing.rotator_client.last_command != command

        client.post('/api/v1/replay/restart').raise_for_status()
        assert replay.demo_pointing.rotator_client.commands == []
        assert len(calls) == 2
