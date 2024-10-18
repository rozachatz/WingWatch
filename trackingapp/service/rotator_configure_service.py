from abc import ABC, abstractmethod

from trackingapp.dao.rotator_client import RotatorClient
from trackingapp.service.coordinate_transform_service import CoordinateTransformService


class AbstractRotatorConfigureService(ABC):

    @abstractmethod
    def transform_and_rotate_antenna(self, coordinates):
        pass


class RotatorConfigureService(AbstractRotatorConfigureService):
    def __init__(self, transformer: CoordinateTransformService, rotator_client: RotatorClient):
        self.transformer = transformer
        self.rotator_client = rotator_client

    async def transform_and_rotate_antenna(self, coordinates):
        azym, el = self.transformer.transform_coordinates(
            float(coordinates[0]),
            float(coordinates[1]),
            float(coordinates[2])
        )
        await self.rotator_client.execute_rotate_command(azym, el)
