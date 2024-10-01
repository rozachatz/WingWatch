import time

from app.dao.AdsbClient import AdsbClient
from app.service.MapService import MapService

api_client = AdsbClient()
map_service = MapService(api_client)

while True:
    map_service.create_map()
    time.sleep(1)