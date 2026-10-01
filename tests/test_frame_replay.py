import asyncio
from datetime import datetime, timezone
import json

from fastapi.testclient import TestClient
import pytest

from trackingapp.main import create_app
from trackingapp.service.frame_replay_source import load_frames
from trackingapp.service.radar_service import RadarService
from trackingapp.demo_fixture_generator import make_frame

EPOCH = datetime(2022, 11, 1, 10, tzinfo=timezone.utc)


def save_frames(directory, indexes=(4,5)):
    directory.mkdir(exist_ok=True)
    for index in indexes:
        frame = make_frame(index,'adapter-export',EPOCH).model_dump(mode='json')
        frame['localization']['note']='Test exported frames, synthetic measurements.'
        (directory/f'frame_{index:04d}.json').write_text(json.dumps(frame))


def test_file_replay_preserves_measurement_time_and_generates_new_session(tmp_path):
    save_frames(tmp_path)
    async def check():
        service=RadarService(directory=tmp_path, interval_seconds=0)
        first=await service.restart()
        assert first.frame_index==4 and first.timestamp.year==2022
        await service._task
        assert service.latest.frame_index==5 and service.paused
        assert service.latest.run_id==first.run_id
        second=await service.restart()
        assert second.run_id!=first.run_id and second.timestamp==first.timestamp
        await service.stop()
    asyncio.run(check())


def test_file_source_is_selected_by_configuration_and_uses_same_api(tmp_path,monkeypatch):
    save_frames(tmp_path)
    monkeypatch.setenv('WINGWATCH_RADAR_FRAMES',str(tmp_path))
    with TestClient(create_app('demo')) as client:
        first=client.get('/api/v1/frames/latest').json()
        assert first['frame_index']==4 and first['timestamp'].startswith('2022-11-01')
        assert client.get('/api/v1/status').json()['source']=='files'
        restarted=client.post('/api/v1/replay/restart').json()
        assert restarted['run_id']!=first['run_id']
        params={'run_id':restarted['run_id'],'frame_index':4}
        assert client.get('/api/v1/tracks/1/contour',params=params).status_code==200


@pytest.mark.parametrize('problem',['mixed_runs','old_schema','duplicate_index','bad_time','nonfinite','wrong_type'])
def test_invalid_exports_are_rejected_before_startup(tmp_path,problem):
    save_frames(tmp_path)
    path=tmp_path/'frame_0005.json';frame=json.loads(path.read_text())
    if problem=='mixed_runs':frame['run_id']='other-run'
    if problem=='old_schema':frame['schema_version']=1
    if problem=='duplicate_index':frame['frame_index']=4
    if problem=='bad_time':frame['timestamp']='2022-11-01T00:00:00Z'
    if problem=='nonfinite':frame['targets'][0]['doppler_hz']=float('nan')
    if problem=='wrong_type':frame['targets'][0]['track_id']='1'
    path.write_text(json.dumps(frame))
    with pytest.raises(ValueError):load_frames(tmp_path)


def test_empty_directory_is_rejected(tmp_path):
    with pytest.raises(ValueError,match='No RadarFrame'):load_frames(tmp_path)
