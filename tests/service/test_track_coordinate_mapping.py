from unittest.mock import AsyncMock, Mock

import pytest

from trackingapp.dao.adsb_client import AdsbClient
from trackingapp.dao.rotator_client import RotatorClient
from trackingapp.service.coordinate_transform_service import CoordinateTransformService
from trackingapp.service.rotator_configure_service import RotatorConfigureService
from trackingapp.service.track_service import TrackService


@pytest.mark.asyncio
async def test_selected_adsb_coordinates_reach_transformer_without_swapping():
    aircraft = {'hex': 'abc001', 'lat': 35.505, 'lon': 24.125, 'altitude': 950}
    response = Mock(status_code=200)
    response.json.return_value = [aircraft]
    adsb = Mock(spec=AdsbClient)
    adsb.getAdsb.return_value = response
    transformer = Mock(spec=CoordinateTransformService)
    transformer.transform_coordinates.return_value = (44.0, 3.0)
    rotator = AsyncMock(spec=RotatorClient)
    service = TrackService(adsb, RotatorConfigureService(transformer, rotator))
    service.select_airplane('abc001')

    assert await service.fetch_data() == [aircraft]

    transformer.transform_coordinates.assert_called_once_with(
        target_lat=35.505, target_lon=24.125, target_el=950.0)
    rotator.execute.assert_awaited_once_with(44.0, 3.0)
