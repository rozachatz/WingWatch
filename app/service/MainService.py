from app.dao.AdsbClient import AdsbClient
from app.dao.RotatorClient import RotatorClient
from app.service.CoordinateTransformService import CoordinateTransformService
from app.service.MapService import MapService


class MainService:
    def __init__(self, api_client: AdsbClient, rotator_client: RotatorClient, map_service: MapService,
                 transformer: CoordinateTransformService) -> None:
        self.api_client = api_client
        self.rotator_client = rotator_client
        self.map_service = map_service
        self.transformer = transformer

    def execute(self):
        data = self.api_client.getAdsb()
        if data:
            self.map_service.create_map(data)
            [azym, el] = self.transformer.transform_coordinates(data[0]['lat'], data[0]['long'], data[0]['el'])
            self.rotator_client.execute(azym, el)
