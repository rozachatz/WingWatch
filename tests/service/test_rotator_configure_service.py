import pytest

from app.dao.rotator_client import RotatorClient
from app.service.coordinate_transform_service import CoordinateTransformService
from app.service.rotator_configure_service import RotatorConfigureService


@pytest.fixture
def coordinate_transform_service():
    return CoordinateTransformService(30.0, 45.0, 120.0)


@pytest.fixture
def mock_rotator_client(mocker):
    # Create a mock RotatorClient
    return mocker.Mock(spec=RotatorClient)


def test_execute(coordinate_transform_service, mock_rotator_client):
    service = RotatorConfigureService(coordinate_transform_service, mock_rotator_client)
    service.execute([30.0, 45.0, 600.0])
    mock_rotator_client.execute.assert_called_once()
