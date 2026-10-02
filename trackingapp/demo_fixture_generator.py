"""Generate the synthetic ten-frame fixture; not a runtime radar source."""
from datetime import datetime, timedelta
import math
import argparse
from pathlib import Path
from datetime import timezone

from trackingapp.service.geographic_coordinates import ecef
from trackingapp.service.range_contour_service import ASSUMED_ALTITUDE_M, range_contour
from trackingapp.models.adsb_models import AdsbAircraft, AdsbFrame, AdsbReplay

from trackingapp.models.radar_models import Localization, RadarFrame, RadarTarget, Site

RECEIVER = Site(name="Demo Malaxa receiver", latitude=35.4669583333,
                longitude=24.0796027778, altitude_m=640)
TRANSMITTER = Site(name="Demo transmitter hypothesis", latitude=35.5319138889,
                   longitude=24.0683722222, altitude_m=111)
FREQUENCY_MHZ = 106.5
SPEED_OF_LIGHT_MPS = 299_792_458.0
FRAME_COUNT = 10


BASELINE_M = math.dist(ecef(RECEIVER), ecef(TRANSMITTER))


def trajectory_position(frame_index: int) -> Site:
    # Vary bearing along shrinking contours for visible, consistent flight motion.
    # This geometric construction creates fixture truth, not radar localization.
    desired_range = 12_500.0 - (frame_index - 2) * 100.0
    bearing = math.pi / 4 + 0.03 * (frame_index - 1)
    lon, lat = range_contour(RECEIVER, TRANSMITTER, desired_range, bearing_offset_rad=bearing)[0]
    return Site(name="Synthetic aircraft", latitude=lat, longitude=lon,
                altitude_m=ASSUMED_ALTITUDE_M)


def path_length(position: Site) -> float:
    xyz = ecef(position)
    return math.dist(xyz, ecef(RECEIVER)) + math.dist(xyz, ecef(TRANSMITTER))


def make_adsb_frame(frame_index: int, epoch: datetime) -> AdsbFrame:
    position = trajectory_position(frame_index)
    timestamp = epoch + timedelta(seconds=frame_index-1)
    return AdsbFrame(frame_index=frame_index, timestamp=timestamp, aircraft=[AdsbAircraft(
        hex="abc001", flight="DEMO01", lat=position.latitude, lon=position.longitude,
        altitude=position.altitude_m, altitude_datum="WGS84 ellipsoid",
        timestamp=timestamp, source="demo_adsb")])


def make_frame(frame_index: int, run_id: str, epoch: datetime) -> RadarFrame:
    if not 1 <= frame_index <= FRAME_COUNT:
        raise ValueError("scenario frames must be between 1 and 10")
    targets = []
    if 2 <= frame_index <= 9:
        misses = max(0, frame_index - 6)
        range_m = round(path_length(trajectory_position(frame_index)), 3)
        next_range = round(path_length(trajectory_position(frame_index+1)), 3)
        range_rate = next_range - range_m
        targets.append(RadarTarget(
            track_id=1,
            status="coasting" if misses else "tentative" if frame_index < 4 else "confirmed",
            bistatic_range_m=range_m, excess_range_m=range_m - BASELINE_M,
            range_rate_mps=range_rate,
            doppler_hz=-range_rate * FREQUENCY_MHZ * 1e6 / SPEED_OF_LIGHT_MPS,
            confidence=None, age_frames=frame_index - 1, misses=misses, position=None,
        ))
    return RadarFrame(
        schema_version=2, run_id=run_id, mode="replay", frame_index=frame_index,
        timestamp=epoch + timedelta(seconds=frame_index - 1),
        frequency_mhz=FREQUENCY_MHZ, receiver=RECEIVER, transmitter=TRANSMITTER,
        localization=Localization(available=False, method="none",
            note="Synthetic radar replay. No geographic target position. Confidence is unavailable; no calibrated score exists."),
        targets=targets, range_doppler_image_url=None,
    )


def generate_fixture(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError("fixture output directory must be empty")
    epoch = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
    adsb_frames = []
    for index in range(1, FRAME_COUNT + 1):
        frame = make_frame(index, "synthetic-ten-frame-fixture", epoch)
        (directory / f"frame_{index:04d}.json").write_text(frame.model_dump_json(indent=2)+"\n")
        adsb_frames.append(make_adsb_frame(index, epoch))
    (directory / "adsb.json").write_text(
        AdsbReplay(schema_version=1, frames=adsb_frames).model_dump_json(indent=2)+"\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate_fixture(args.output)
    print(f"Generated {FRAME_COUNT} synchronized radar and demo ADS-B frames in {args.output}")


if __name__ == "__main__":
    main()
