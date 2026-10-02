"""Aircraft reports and selection endpoints."""
from fastapi import APIRouter, HTTPException, Query, Request

from trackingapp.models.pointing_models import DemoPointingStatus

router = APIRouter(tags=["aircraft"])


@router.get("/api/aircraft")
async def get_aircraft(request: Request, run_id: str | None = None, frame_index: int | None = Query(default=None, ge=0)):
    radar = request.app.state.radar_service
    if request.app.state.track_service is None:
        if (run_id is None) != (frame_index is None):
            raise HTTPException(422, "run_id and frame_index must be supplied together")
        if run_id is not None and (radar.latest is None or radar.latest.run_id != run_id
                                  or radar.latest.frame_index != frame_index):
            raise HTTPException(409, "snapshot_changed")
        return radar.current_aircraft()
    return await request.app.state.track_service.fetch_data()

@router.post("/api/select_aircraft/{hex_id}")
async def select_aircraft(hex_id: str, request: Request) -> str:
    if request.app.state.track_service is None:
        radar = request.app.state.radar_service
        if not radar.adsb_frames or radar.latest is None:
            raise HTTPException(409, 'Demo ADS-B reports unavailable')
        try:
            await radar.demo_pointing.select(hex_id, radar.latest, radar.current_aircraft())
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc
        return f'Tracking demo aircraft {hex_id.lower()}'
    return request.app.state.track_service.select_airplane(hex_id)


@router.get('/api/v1/pointing', response_model=DemoPointingStatus)
async def pointing_status(request: Request, run_id: str, frame_index: int = Query(ge=0)):
    if request.app.state.track_service is not None:
        raise HTTPException(409, 'Simulated pointing is available in demo mode')
    radar = request.app.state.radar_service
    frame = radar.latest
    if frame is None or not radar.adsb_frames:
        raise HTTPException(404, 'Demo ADS-B reports unavailable')
    if frame.run_id != run_id or frame.frame_index != frame_index:
        raise HTTPException(409, 'snapshot_changed')
    return radar.demo_pointing.current
