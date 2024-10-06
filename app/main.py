import time

from app.dao.AdsbClient import AdsbClient
from app.dao.RotatorClient import RotatorClient
from app.service.MainService import MainService
from app.service.MapService import MapService

api_client = AdsbClient()
map_service = MapService()
rotator_client = RotatorClient()
main_service = MainService(api_client, rotator_client, map_service)

while True:
    rotator_client.set_rotator()
    time.sleep(5)