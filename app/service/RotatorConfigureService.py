from app.dao.RotatorClient import RotatorClient
from app.service import CoordinateTransformService


class RotatorConfigureService:
    def __init__(self, client: RotatorClient, transformer: CoordinateTransformService):
        self.transformer = transformer
        self.client = client

    def execute(self, coordinates):
        azym, el = self.transformer.transform_coordinates(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]))
        self.client.execute(azym, el)
