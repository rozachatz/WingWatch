import time

import pytest
from testcontainers.compose import DockerCompose

from trackingapp.dao.adsb_client import AdsbClient
from trackingapp.dao.rotator_client import RotatorClient
from trackingapp.service.coordinate_transform_service import CoordinateTransformService
from trackingapp.service.rotator_configure_service import RotatorConfigureService
from trackingapp.service.track_service import TrackService


@pytest.fixture
def mock_adsb_client(mocker):
    # Create a mock AdsbClient
    return mocker.Mock(spec=AdsbClient)


@pytest.fixture
def rotator_service(client, coordinates):
    return RotatorConfigureService(coordinates, client)


@pytest.fixture(scope="session")
def client():
    return RotatorClient()


@pytest.fixture(scope="session")
def coordinates():
    return CoordinateTransformService(50, 50, 100)


@pytest.fixture(scope="session")  # Explicitly set the loop scope
def fastapi_container():
    print("Starting fastapi_container fixture...")  # Debug print
    compose = DockerCompose(".", services=["hamlib"])
    compose.start()
    print("Container started.")
    time.sleep(5)
    yield
    compose.stop()

# Full IT Test
@pytest.mark.asyncio
async def test_track_service_execute(mock_adsb_client, rotator_service, client, fastapi_container):
    await client.connect()
    # Mock the response of getAdsb
    i = 0
    lon = 5
    lat = 15
    while i < 10:
        mock_adsb_client.getAdsb.return_value.json.return_value = [
            {"lon": lon, "lat": lat, "altitude": 3000, "hex": "HSA23D"}]
        mock_adsb_client.getAdsb.return_value.status_code = 200

        track_service = TrackService(mock_adsb_client, rotator_service)
        track_service.select_airplane("HSA23D")
        await track_service.fetch_data()
        lon = lon + i
        lat = lat + 2 * i
        i = i + 1

    # Assertions
    await client.disconnect()
    await client.execute(0, 0)
