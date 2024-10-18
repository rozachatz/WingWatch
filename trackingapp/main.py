import logging
import os

from fastapi import FastAPI
from fastapi.params import Depends
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from trackingapp.configuration.settings import Settings
from trackingapp.dao.adsb_client import AdsbClient
from trackingapp.dao.rotator_client import RotatorClient
from trackingapp.service.coordinate_transform_service import CoordinateTransformService
from trackingapp.service.rotator_configure_service import RotatorConfigureService
from trackingapp.service.track_service import TrackService

# Initializations
trackingapp = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_settings():
    return Settings()


async def track_service(settings: Settings = Depends(get_settings)):
    transformer = CoordinateTransformService(settings.latitude, settings.longitude, settings.altitude)
    rotator_client = RotatorClient()
    rotator_service = RotatorConfigureService(transformer, rotator_client)
    api_client = AdsbClient()
    return TrackService(api_client, rotator_service)


@trackingapp.get("/")
async def read_root():
    trackingapp.mount("/static", StaticFiles(directory="static"), name="static")
    file_path = os.path.join(os.path.dirname(__file__), '../static/map.html')
    return FileResponse(file_path)


@trackingapp.get("/api/aircraft")
async def get_aircraft(service: TrackService = Depends(track_service)):
    return await service.fetch_data()


@trackingapp.post("/api/select_aircraft/{hex_id}")
def select_aircraft(hex_id: str, service: TrackService = Depends(track_service)) -> str:
    return service.select_airplane(hex_id)
