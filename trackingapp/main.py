import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from trackingapp.api.aircraft import router as aircraft_router
from trackingapp.api.radar import router as radar_router
from trackingapp.service.radar_service import RadarService

ROOT = Path(__file__).resolve().parent.parent


def create_app(mode: str | None = None, radar_service: RadarService | None = None) -> FastAPI:
    mode = mode or os.getenv("WINGWATCH_MODE", "demo")
    if mode not in {"demo", "hardware"}:
        raise ValueError("WINGWATCH_MODE must be demo or hardware")
    directory = os.getenv("WINGWATCH_RADAR_FRAMES")
    radar = radar_service
    if radar is None and (mode == "demo" or directory):
        radar = RadarService(directory=Path(directory) if directory else None)

    @asynccontextmanager
    async def lifespan(app):
        app.state.track_service = None
        if mode == "hardware":
            from dotenv import find_dotenv, load_dotenv
            from trackingapp.dao.adsb_client import AdsbClient
            from trackingapp.dao.rotator_client import RotatorClient
            from trackingapp.service.coordinate_transform_service import CoordinateTransformService
            from trackingapp.service.rotator_configure_service import RotatorConfigureService
            from trackingapp.service.track_service import TrackService

            load_dotenv(find_dotenv(f'.env.{os.getenv("ENV", "secrets")}'))
            transformer = CoordinateTransformService(
                float(os.environ["LATITUDE"]), float(os.environ["LONGITUDE"]),
                float(os.environ["ALTITUDE"]))
            app.state.track_service = TrackService(
                AdsbClient(), RotatorConfigureService(transformer, RotatorClient()))
        if radar is not None:
            await radar.restart()
        try:
            yield
        finally:
            if radar is not None:
                await radar.stop()

    app = FastAPI(lifespan=lifespan)
    app.state.radar_service = radar
    app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

    @app.get("/")
    async def read_root():
        return FileResponse(ROOT / "static" / "map.html")

    app.include_router(aircraft_router)
    app.include_router(radar_router)

    return app


trackingapp = create_app()
