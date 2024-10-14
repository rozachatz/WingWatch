from app.dao.AdsbClient import AdsbClient
from app.service import RotatorConfigureService
from app.service.MapService import MapService


class TrackService:
    def __init__(self, api_client: AdsbClient, rotator_service: RotatorConfigureService,
                 map_service: MapService) -> None:
        self.api_client = api_client
        self.rotator_service = rotator_service
        self.map_service = map_service

    def execute(self):
        data = self.api_client.getAdsb().json()
        if data:
            self.map_service.create_map(data) #illustration purposes
            first_element = data[0] # for now, track only the first element, locking technique
            self.rotator_service.execute(first_element['lon'], first_element['lat'], first_element['altitude'])
