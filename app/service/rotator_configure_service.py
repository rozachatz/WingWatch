from app.dao.rotator_client import RotatorClient
from app.service.coordinate_transform_service import CoordinateTransformService


class RotatorConfigureService:
    def __init__(self, transformer: CoordinateTransformService, rotator_client: RotatorClient):
        self.transformer = transformer
        self.rotator_client = rotator_client

    def execute(self, coordinates):
        azym, el = self.transformer.transform_coordinates(float(coordinates[0]), float(coordinates[1]),
                                                          float(coordinates[2]))
        self.rotator_client.execute(azym, el)
