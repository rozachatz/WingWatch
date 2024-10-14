import os
import time

from dotenv import load_dotenv, find_dotenv

from app.dao.AdsbClient import AdsbClient
from app.dao.RotatorClient import RotatorClient
from app.service.CoordinateTransformService import CoordinateTransformService
from app.service.MapService import MapService
from app.service.RotatorConfigureService import RotatorConfigureService
from app.service.TrackService import TrackService

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

track_service = TrackService(api_client, rotator_client, map_service)
while True:
    track_service.execute()
    time.sleep(1)
