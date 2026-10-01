"""Replay validated Malaxa RadarFrame v2 exports without radar hardware."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from trackingapp.models.radar_models import RadarFrame


def load_frames(directory: Path) -> list[RadarFrame]:
    files = list(directory.glob('frame_*.json'))
    if not files:
        raise ValueError(f'No RadarFrame exports found in {directory}')
    schema_path = Path(__file__).parents[1]/'models/radar-frame.schema.json'
    validator = Draft202012Validator(json.loads(schema_path.read_text()), format_checker=FormatChecker())
    frames = []
    for path in files:
        try:
            payload = json.loads(path.read_text())
            validator.validate(payload)
            frames.append(RadarFrame.model_validate(payload))
        except (OSError, ValueError, ValidationError) as exc:
            # Include the filename; reject the entire source rather than skipping bad frames.
            raise ValueError(f'Invalid RadarFrame in {path.name}: {exc}') from exc
    frames.sort(key=lambda frame: frame.frame_index)
    if len({frame.run_id for frame in frames}) != 1:
        raise ValueError('Replay directory contains multiple radar runs')
    if len({frame.frame_index for frame in frames}) != len(frames):
        raise ValueError('Replay contains duplicate frame indexes')
    if any(frame.mode != 'replay' for frame in frames):
        raise ValueError('File source requires replay-mode frames')
    if any(b.timestamp <= a.timestamp for a, b in zip(frames, frames[1:])):
        raise ValueError('Replay measurement timestamps must increase with frame indexes')
    return frames



def load_adsb(directory: Path, radar_frames: list[RadarFrame]) -> dict:
    from trackingapp.models.adsb_models import AdsbReplay

    path = directory / 'adsb.json'
    if not path.exists():
        return {}
    replay = AdsbReplay.model_validate_json(path.read_text())
    by_index = {frame.frame_index: frame for frame in replay.frames}
    if len(by_index) != len(replay.frames):
        raise ValueError('ADS-B replay has duplicate frame indexes')
    radar_by_index = {frame.frame_index: frame for frame in radar_frames}
    if set(by_index) != set(radar_by_index):
        raise ValueError('ADS-B snapshots must cover exactly the loaded radar frames')
    for index, frame in by_index.items():
        if frame.timestamp != radar_by_index[index].timestamp:
            raise ValueError('ADS-B snapshot time must match its radar frame')
        if any(aircraft.timestamp != frame.timestamp for aircraft in frame.aircraft):
            raise ValueError('ADS-B reports must match their snapshot time')
        if len({aircraft.hex.lower() for aircraft in frame.aircraft}) != len(frame.aircraft):
            raise ValueError('duplicate ADS-B aircraft in a snapshot')
    return by_index
