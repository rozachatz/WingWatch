import logging
import os

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from trackingapp.dao.adsb_client import AdsbClient
from trackingapp.dao.rotator_client import RotatorClient
from trackingapp.service.coordinate_transform_service import CoordinateTransformService
from trackingapp.service.rotator_configure_service import RotatorConfigureService
from trackingapp.service.track_service import TrackService

# Initializations
env_file = find_dotenv(f'.env.{os.getenv("ENV", "secrets")}')
load_dotenv(env_file)
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
altitude = os.getenv("ALTITUDE")
transformer = CoordinateTransformService(float(latitude), float(longitude), float(altitude))
rotator_client = RotatorClient()
rotator_service = RotatorConfigureService(transformer, rotator_client)
api_client = AdsbClient()
track_service = TrackService(api_client, rotator_service)

trackingapp = FastAPI()
trackingapp.mount("/static", StaticFiles(directory="static"), name="static")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@trackingapp.get("/")
async def read_root():
    file_path = os.path.join(os.path.dirname(__file__), '../static/map.html')
    return FileResponse(file_path)


@trackingapp.get("/api/aircraft")
async def get_aircraft():
    all_aircraft = await track_service.fetch_data()
    return all_aircraft


@trackingapp.post("/api/select_aircraft/{hex_id}")
def select_aircraft(hex_id: str) -> str:
    message = track_service.select_airplane(hex_id)
    return message
