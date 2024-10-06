from app.dao.AdsbClient import AdsbClient
from app.dao.RotatorClient import RotatorClient
from app.service.MapService import MapService


class MainService:
    def __init__(self, api_client: AdsbClient, rotator_client: RotatorClient, map_service: MapService) -> None:
        self.api_client = api_client
        self.rotator_client = rotator_client
        self.map_service = map_service

    def execute(self):
        data = self.api_client.getAdsb()
        if data:
            self.map_service.create_map(data)
            self.rotator_client.execute()


