import asyncio
from asyncio.log import logger

from trackingapp.dao.adsb_client import AdsbClient
from trackingapp.service.rotator_configure_service import RotatorConfigureService


def print_results(all_aircraft_data):
    for aircraft in all_aircraft_data:
        print(
            f"Hex: {aircraft['hex']}, Latitude: {aircraft['lat']}, Longitude: {aircraft['lon']}, Altitude: {aircraft['altitude']}")
    print(
        "---------------------------------------------------------------------------------------------------------------------")


class TrackService:
    def __init__(self, api_client: AdsbClient, rotator_service: RotatorConfigureService) -> None:
        self.selected_hex_id = None
        self.api_client = api_client
        self.rotator_service = rotator_service


    def select_airplane(self, hex_id: str) -> str:
        self.selected_hex_id = hex_id
        return f"Tracking airplane {hex_id}"

    async def fetch_data(self):
        try:

            logger.info("Fetching data...")

            # Run the synchronous getAdsb method in a separate thread and await the result
            response = await asyncio.to_thread(self.api_client.getAdsb)

            # Check if the response is valid before calling .json()
            if response.status_code == 200:

                all_aircraft_data = response.json()
                print_results(all_aircraft_data)
                if self.selected_hex_id:
                    selected_aircraft = next(
                        (aircraft for aircraft in all_aircraft_data if aircraft['hex'] == self.selected_hex_id),
                        None
                    )
                    if selected_aircraft:
                        logger.info("Selected aircraft data: %s", selected_aircraft)
                        await self.rotator_service.execute_async(
                            [selected_aircraft['lon'], selected_aircraft['lat'], selected_aircraft['altitude']]
                        )
                    else:
                        logger.warning("No aircraft found with hex ID: %s", self.selected_hex_id)
                return all_aircraft_data

            else:
                logger.error("Failed to fetch aircraft data, status code: %d", response.status_code)

        except Exception as e:
            logger.error("Error fetching aircraft data: %s", e, exc_info=True)

