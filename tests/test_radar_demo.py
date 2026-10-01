import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
import pytest
from pydantic import ValidationError

from trackingapp.main import create_app
from trackingapp.models.radar_models import RadarFrame
from trackingapp.service.radar_service import RadarService
from trackingapp.demo_fixture_generator import BASELINE_M, make_frame

EPOCH = datetime(2026, 10, 1, tzinfo=timezone.utc)
SCHEMA = json.loads((Path(__file__).parents[1] / 'trackingapp/models/radar-frame.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def test_scenario_contract_and_lifecycle():
    frames = [make_frame(i, 'demo', EPOCH) for i in range(1, 11)]
    for frame in frames:
        VALIDATOR.validate(frame.model_dump(mode='json', exclude_unset=True))
    assert frames[0].targets == frames[9].targets == []
    assert [f.targets[0].status for f in frames[1:9]] == [
        'tentative', 'tentative', 'confirmed', 'confirmed', 'confirmed',
        'coasting', 'coasting', 'coasting']
    for previous, current in zip(frames[1:8], frames[2:9]):
        a, b = previous.targets[0], current.targets[0]
        assert b.bistatic_range_m - a.bistatic_range_m == -100
        assert b.age_frames == a.age_frames + 1
        assert b.excess_range_m == pytest.approx(b.bistatic_range_m - BASELINE_M)
        assert b.doppler_hz == pytest.approx(-b.range_rate_mps * 106.5e6 / 299792458)
        assert b.position is None
    assert [f.targets[0].misses for f in frames[6:9]] == [1, 2, 3]


def test_replay_finishes_and_restart_changes_identity():
    async def check():
        service = RadarService(interval_seconds=0)
        first = await service.restart()
        await service._task
        assert service.paused and service.latest.frame_index == 10
        restarted = await service.restart()
        assert restarted.run_id != first.run_id
        assert restarted.frame_index == 1
        await service.stop()
    asyncio.run(check())


def test_demo_api_starts_without_hardware_and_stops_background_task(monkeypatch):
    for name in ['LATITUDE', 'LONGITUDE', 'ALTITUDE']:
        monkeypatch.delenv(name, raising=False)
    service = RadarService(interval_seconds=3600)
    with TestClient(create_app('demo', service)) as client:
        assert client.get('/api/aircraft').json()[0]['source'] == 'demo_adsb'
        response = client.get('/api/v1/frames/latest')
        assert response.status_code == 200
        VALIDATOR.validate(response.json())
        old_id = response.json()['run_id']
        restarted = client.post('/api/v1/replay/restart').json()
        VALIDATOR.validate(restarted)
        assert restarted['run_id'] != old_id
        assert restarted['frame_index'] == 1
        assert client.get('/api/v1/status').json()['source_connected'] is True
        assert client.post('/api/select_aircraft/test').status_code == 409
    assert service._task is None


def test_invalid_frames_are_rejected():
    frame = make_frame(2, 'demo', EPOCH).model_dump(mode='json')
    frame['targets'][0]['doppler_hz'] = float('nan')
    with pytest.raises(ValidationError):
        RadarFrame.model_validate(frame)
    with pytest.raises(ValidationError):
        make_frame(2, 'demo', datetime(2026, 10, 1))


def test_v2_unknown_confidence_and_required_numeric_frequency():
    frame = make_frame(2, 'demo', EPOCH)
    assert frame.schema_version == 2
    assert frame.targets[0].confidence is None
    payload = frame.model_dump(mode='json')
    VALIDATOR.validate(payload)
    payload['frequency_mhz'] = None
    with pytest.raises(ValidationError):
        RadarFrame.model_validate(payload)


def test_bundled_fixture_matches_generated_scenario():
    from trackingapp.service.radar_service import DEFAULT_FRAMES
    from trackingapp.service.frame_replay_source import load_frames
    frames = load_frames(DEFAULT_FRAMES)
    assert len(frames) == 10
    for frame in frames:
        generated = make_frame(frame.frame_index, frame.run_id, EPOCH.replace(hour=12))
        assert frame.model_dump() == generated.model_dump()
