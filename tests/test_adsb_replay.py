import json
import math
from datetime import datetime, timezone

from fastapi.testclient import TestClient
import pytest

from trackingapp.demo_fixture_generator import FRAME_COUNT, generate_fixture, path_length
from trackingapp.main import create_app
from trackingapp.models.radar_models import Site
from trackingapp.service.geographic_coordinates import ecef
from trackingapp.service.radar_service import DEFAULT_FRAMES, RadarService
from trackingapp.service.frame_replay_source import load_adsb, load_frames


def test_common_trajectory_matches_radar_range_and_doppler():
    frames=load_frames(DEFAULT_FRAMES)
    adsb=load_adsb(DEFAULT_FRAMES,frames)
    assert len(adsb)==FRAME_COUNT
    ranges=[]
    for frame in frames:
        report=adsb[frame.frame_index].aircraft[0]
        assert report.timestamp==frame.timestamp
        site=Site(name='aircraft',latitude=report.lat,longitude=report.lon,altitude_m=report.altitude)
        xyz=ecef(site)
        length=math.dist(xyz,ecef(frame.receiver))+math.dist(xyz,ecef(frame.transmitter))
        ranges.append(length)
        if frame.targets:
            track=frame.targets[0]
            assert track.bistatic_range_m==pytest.approx(length,abs=0.001)
            assert track.position is None
    for index,frame in enumerate(frames[:-1]):
        if frame.targets:
            rate=(ranges[index+1]-ranges[index])/(frames[index+1].timestamp-frame.timestamp).total_seconds()
            assert frame.targets[0].range_rate_mps==pytest.approx(rate,abs=0.001)
            assert frame.targets[0].doppler_hz==pytest.approx(-rate*frame.frequency_mhz*1e6/299792458,abs=0.001)


def test_aircraft_api_tracks_replay_and_restart():
    service=RadarService(interval_seconds=3600)
    with TestClient(create_app('demo',service)) as client:
        radar=client.get('/api/v1/frames/latest').json()
        first=client.get('/api/aircraft').json()[0]
        assert first['source']=='demo_adsb' and first['flight']=='DEMO01'
        assert first['timestamp']==radar['timestamp']
        params={'run_id':radar['run_id'],'frame_index':radar['frame_index']}
        assert client.get('/api/aircraft',params=params).status_code==200
        assert client.get('/api/aircraft',params={**params,'frame_index':99}).status_code==409
        client.post('/api/v1/replay/restart')
        assert client.get('/api/aircraft').json()[0]==first
        assert client.get('/api/aircraft',params=params).status_code==409


@pytest.mark.parametrize('problem',['time','coverage','duplicate'])
def test_bad_adsb_alignment_is_rejected(tmp_path,problem):
    generate_fixture(tmp_path)
    path=tmp_path/'adsb.json';payload=json.loads(path.read_text())
    if problem=='time':payload['frames'][0]['timestamp']='2026-10-01T01:00:00Z'
    if problem=='coverage':payload['frames'].pop()
    if problem=='duplicate':payload['frames'].append(payload['frames'][0])
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):RadarService(directory=tmp_path)


def test_demo_aircraft_has_visible_motion_and_stays_on_selected_contour():
    frames=load_frames(DEFAULT_FRAMES)
    adsb=load_adsb(DEFAULT_FRAMES,frames)
    xyz=[]
    for frame in frames:
        aircraft=adsb[frame.frame_index].aircraft[0]
        site=Site(name='aircraft',latitude=aircraft.lat,longitude=aircraft.lon,altitude_m=aircraft.altitude)
        xyz.append(ecef(site))
    assert math.dist(xyz[0],xyz[-1]) > 1000
    assert all(50 < math.dist(a,b) < 300 for a,b in zip(xyz,xyz[1:]))
