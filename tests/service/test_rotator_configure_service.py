from unittest.mock import AsyncMock

import pytest

from trackingapp.dao.rotator_client import RotatorClient
from trackingapp.service.coordinate_transform_service import CoordinateTransformService
from trackingapp.service.rotator_configure_service import RotatorConfigureService


@pytest.fixture
def coordinate_transform_service():
    return CoordinateTransformService(30.0, 45.0, 120.0)


@pytest.fixture
def mock_rotator_client():
    # Create a mock RotatorClient
    return AsyncMock(spec=RotatorClient)


@pytest.mark.asyncio
async def test_execute(coordinate_transform_service, mock_rotator_client):
    service = RotatorConfigureService(coordinate_transform_service, mock_rotator_client)
    await service.transform_and_rotate_antenna([30.0, 45.0, 600.0])
    await service.transform_and_rotate_antenna([0, 0, 0])
