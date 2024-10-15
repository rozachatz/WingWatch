import asyncio
import os
from time import sleep

from dotenv import load_dotenv, find_dotenv

from trackingapp.dao.adsb_client import AdsbClient
from trackingapp.dao.rotator_client import RotatorClient
from trackingapp.service.coordinate_transform_service import CoordinateTransformService
from trackingapp.service.map_service import MapService
from trackingapp.service.rotator_configure_service import RotatorConfigureService
from trackingapp.service.track_service import TrackService

env_file = find_dotenv(f'.env.{os.getenv("ENV", "secrets")}')
load_dotenv(env_file)
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
altitude = os.getenv("ALTITUDE")
transformer = CoordinateTransformService(float(latitude), float(longitude), float(altitude))
rotator_client = RotatorClient()
rotator_service = RotatorConfigureService(transformer, rotator_client)
api_client = AdsbClient()
map_service = MapService()
track_service = TrackService(api_client, rotator_service)


def data_fetching_loop():
    while True:
        track_service.fetch_data()
        sleep(1)

data_fetching_loop()
