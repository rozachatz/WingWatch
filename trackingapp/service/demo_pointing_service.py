"""Drive the real pointing service with demo reports and a simulated rotator."""
from trackingapp.dao.simulated_rotator_client import SimulatedRotatorClient
from trackingapp.models.adsb_models import AdsbAircraft
from trackingapp.models.pointing_models import DemoPointingStatus
from trackingapp.models.radar_models import RadarFrame
from trackingapp.service.coordinate_transform_service import CoordinateTransformService
from trackingapp.service.rotator_configure_service import RotatorConfigureService


class DemoPointingService:
    def __init__(self) -> None:
        self.selected_hex_id: str | None = None
        self.rotator_client = SimulatedRotatorClient()
        self.current: DemoPointingStatus | None = None

    async def restart(self, frame: RadarFrame, aircraft: list[AdsbAircraft]) -> None:
        self.selected_hex_id = None
        self.rotator_client.reset()
        await self.advance(frame, aircraft)

    async def select(self, hex_id: str, frame: RadarFrame, aircraft: list[AdsbAircraft]) -> None:
        if not any(item.hex.lower() == hex_id.lower() for item in aircraft):
            raise ValueError('aircraft_not_found')
        self.selected_hex_id = hex_id.lower()
        await self.advance(frame, aircraft)

    async def advance(self, frame: RadarFrame, aircraft: list[AdsbAircraft]) -> None:
        report = next((item for item in aircraft if item.hex.lower() == self.selected_hex_id), None)
        status = 'idle' if self.selected_hex_id is None else 'commanded' if report else 'no_report'
        azimuth = elevation = None
        if report is not None:
            receiver = frame.receiver
            transformer = CoordinateTransformService(
                receiver.latitude, receiver.longitude, receiver.altitude_m)
            service = RotatorConfigureService(transformer, self.rotator_client)
            await service.execute_async(
                latitude=report.lat, longitude=report.lon, altitude_m=report.altitude)
            azimuth, elevation = self.rotator_client.last_command
        self.current = DemoPointingStatus(
            source='demo_adsb', run_id=frame.run_id, frame_index=frame.frame_index,
            receiver=frame.receiver, selected_hex=self.selected_hex_id,
            selected_flight=report.flight if report else None, status=status,
            command_azimuth_deg=azimuth, command_elevation_deg=elevation,
        )
