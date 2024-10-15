from trackingapp.dao.adsb_client import AdsbClient

from trackingapp.service.rotator_configure_service import RotatorConfigureService


class TrackService:
    def __init__(self, api_client: AdsbClient, rotator_service: RotatorConfigureService) -> None:
        self.selected_hex_id = None
        self.api_client = api_client
        self.rotator_service = rotator_service

    def select_airplane(self, hex_id: str):
        self.selected_hex_id = hex_id
        return {'message': f'Tracking airplane {hex_id}'}

    def fetch_data(self):
        try:
            all_aircraft_data = (self.api_client.getAdsb()).json()  # Ensure this is awaited
            if self.selected_hex_id:
                selected_aircraft = next(
                    (aircraft for aircraft in all_aircraft_data if aircraft['hex'] == self.selected_hex_id),
                    None
                )
                if selected_aircraft:
                    self.rotator_service.execute(
                        [selected_aircraft['lon'], selected_aircraft['lat'], selected_aircraft['altitude']])
                else:
                    print(f"No aircraft found with hex ID: {self.selected_hex_id}")

        except Exception as e:
            print(f"Error fetching aircraft data: {e}")
