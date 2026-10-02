"""Radar snapshots, replay controls, status and contour endpoints."""
from fastapi import APIRouter, HTTPException, Query, Request

from trackingapp.models.radar_models import RadarFrame, RadarStatus

router = APIRouter(tags=["radar"])


def radar_service(request: Request):
    radar = request.app.state.radar_service
    if radar is None:
        raise HTTPException(503, "radar_unavailable")
    return radar


@router.get("/api/v1/frames/latest", response_model=RadarFrame, response_model_exclude_none=False)
async def latest_frame(request: Request):
    radar = radar_service(request)
    if radar.latest is None:
        raise HTTPException(404, "frame_not_found")
    return radar.latest

@router.get("/api/v1/tracks/{track_id}/contour")
async def track_contour(track_id: int, request: Request, run_id: str, frame_index: int = Query(ge=0)):
    from trackingapp.service.range_contour_service import ASSUMED_ALTITUDE_M, range_contour

    radar = radar_service(request)
    frame = radar.latest
    if frame is None:
        raise HTTPException(404, "frame_not_found")
    if frame.run_id != run_id or frame.frame_index != frame_index:
        raise HTTPException(409, "snapshot_changed")
    target = next((t for t in frame.targets if t.track_id == track_id), None)
    if target is None:
        raise HTTPException(404, "track_not_found")
    try:
        coordinates = range_contour(frame.receiver, frame.transmitter, target.bistatic_range_m)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [coordinates]},
            "properties": {"run_id": frame.run_id, "frame_index": frame.frame_index,
                           "track_id": track_id, "status": target.status,
                           "assumed_altitude_m": ASSUMED_ALTITUDE_M,
                           "altitude_datum": "WGS84 ellipsoid", "position_estimate": False}}

@router.post("/api/v1/replay/restart", response_model=RadarFrame)
async def restart_replay(request: Request):
    radar = radar_service(request)
    return await radar.restart()

@router.get("/api/v1/status", response_model=RadarStatus)
async def radar_status(request: Request):
    radar = radar_service(request)
    latest = radar.latest
    return {"service_status": "ok", "mode": "replay", "source": radar.source,
            "run_id": latest.run_id if latest else None,
            "latest_frame_index": latest.frame_index if latest else None,
            "last_update_utc": latest.timestamp if latest else None,
            "source_connected": latest is not None, "paused": radar.paused,
            "error": None}
