import asyncio
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


async def main_coroutine():
    await rotator_client.connect()
    await rotator_client.execute(0, 0)
    try:
        while True:
            await track_service.fetch_data()
            await asyncio.sleep(1)
    finally:
        await rotator_client.disconnect()  # Ensure disconnection on exit


async def start_background_task():
    asyncio.create_task(main_coroutine())


# Immediately start the background task using the existing loop
loop = asyncio.get_event_loop()
loop.create_task(start_background_task())


@trackingapp.get("/")
async def read_root():
    file_path = os.path.join(os.path.dirname(__file__), '../static/map.html')
    return FileResponse(file_path)


@trackingapp.get("/api/aircraft")
async def get_aircraft():
    return track_service.all_aircraft_data


@trackingapp.post("/api/select_aircraft/{hex_id}")
def select_aircraft(hex_id: str) -> str:
    message = track_service.select_airplane(hex_id)
    return message


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(trackingapp, host="0.0.0.0", port=8000)
