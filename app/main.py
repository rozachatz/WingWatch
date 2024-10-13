import os
import time

from dotenv import load_dotenv, find_dotenv

from app.dao.AdsbClient import AdsbClient
from app.dao.RotatorClient import RotatorClient
from app.service.CoordinateTransformService import CoordinateTransformService
from app.service.MainService import MainService
from app.service.MapService import MapService

env_file = find_dotenv(f'.env.{os.getenv("ENV", "secrets")}')
load_dotenv(env_file)
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
altitude = os.getenv("ALTITUDE")

api_client = AdsbClient()
map_service = MapService()
rotator_client = RotatorClient()
service = CoordinateTransformService(float(latitude), float(longitude), float(altitude))
main_service = MainService(api_client, rotator_client, map_service, service)
while True:
    main_service.execute()
    time.sleep(1)
