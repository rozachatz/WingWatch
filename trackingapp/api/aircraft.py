"""Aircraft reports and selection endpoints."""
from fastapi import APIRouter, HTTPException, Query, Request

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
def select_aircraft(hex_id: str, request: Request) -> str:
    if request.app.state.track_service is None:
        raise HTTPException(409, "Aircraft selection requires hardware mode")
    return request.app.state.track_service.select_airplane(hex_id)
