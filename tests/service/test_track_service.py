import pytest

from app.dao.adsb_client import AdsbClient
from app.service.map_service import MapService
from app.service.rotator_configure_service import RotatorConfigureService
from app.service.track_service import TrackService


@pytest.fixture
def mock_adsb_client(mocker):
    # Create a mock AdsbClient
    return mocker.Mock(spec=AdsbClient)


@pytest.fixture
def mock_rotator_service(mocker):
    return mocker.Mock(spec=RotatorConfigureService)


@pytest.fixture
def mock_map_service(mocker):
    return mocker.Mock(MapService())


def test_track_service_execute(mock_adsb_client, mock_rotator_service, mock_map_service):
    # Mock the response of getAdsb
    mock_adsb_client.getAdsb.return_value.json.return_value = [{"lon": 10.0, "lat": 20.0, "altitude": 3000}]

    track_service = TrackService(mock_adsb_client, mock_rotator_service, mock_map_service)
    track_service.execute()

    # Assertions
    mock_adsb_client.getAdsb.assert_called_once()
    mock_map_service.create_map.assert_called_once_with(mock_adsb_client.getAdsb.return_value.json.return_value)
    mock_rotator_service.execute.assert_called_once_with([10.0, 20.0, 3000])
