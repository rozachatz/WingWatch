from trackingapp.dao.rotator_client import RotatorClient

from trackingapp.service.coordinate_transform_service import CoordinateTransformService


class RotatorConfigureService:
    def __init__(self, transformer: CoordinateTransformService, rotator_client: RotatorClient):
        self.transformer = transformer
        self.rotator_client = rotator_client

    async def execute_async(self, *, latitude: float, longitude: float, altitude_m: float):
        azym, el = self.transformer.transform_coordinates(
            target_lat=float(latitude),
            target_lon=float(longitude),
            target_el=float(altitude_m),
        )
        await self.rotator_client.execute(azym, el)
