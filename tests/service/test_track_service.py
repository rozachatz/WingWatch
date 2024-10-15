import pytest

from trackingapp.dao.adsb_client import AdsbClient
from trackingapp.service.rotator_configure_service import RotatorConfigureService
from trackingapp.service.track_service import TrackService


@pytest.fixture
def mock_adsb_client(mocker):
    # Create a mock AdsbClient
    return mocker.Mock(spec=AdsbClient)


@pytest.fixture
def mock_rotator_service(mocker):
    return mocker.Mock(spec=RotatorConfigureService)


@pytest.mark.asyncio
async def test_track_service_execute(mock_adsb_client, mock_rotator_service):
    # Mock the response of getAdsb
    mock_adsb_client.getAdsb.return_value.json.return_value = [
        {"lon": 10.0, "lat": 20.0, "altitude": 3000, "hex": "HSA23D"}]

    track_service = TrackService(mock_adsb_client, mock_rotator_service)
    track_service.select_airplane("HSA23D")
    await track_service.fetch_data()

    # Assertions
    mock_adsb_client.getAdsb.assert_called_once()
    mock_rotator_service.execute.assert_called_once_with([10.0, 20.0, 3000])
