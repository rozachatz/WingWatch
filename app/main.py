import os
import time

from dotenv import load_dotenv, find_dotenv

from app.dao.adsb_client import AdsbClient
from app.dao.rotator_client import RotatorClient
from app.service.coordinate_transform_service import CoordinateTransformService
from app.service.map_service import MapService
from app.service.rotator_configure_service import RotatorConfigureService
from app.service.track_service import TrackService

env_file = find_dotenv(f'.env.{os.getenv("ENV", "secrets")}')
load_dotenv(env_file)
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
altitude = os.getenv("ALTITUDE")

transformer = CoordinateTransformService(float(latitude), float(longitude), float(altitude))
rotator_client = RotatorClient()
rotator_service = RotatorConfigureService(rotator_client, transformer)

api_client = AdsbClient()
map_service = MapService()

track_service = TrackService(api_client, RotatorClient, map_service)
while True:
    track_service.execute()
    time.sleep(1)
