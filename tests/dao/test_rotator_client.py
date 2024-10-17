import time

import pytest
from testcontainers.compose import DockerCompose

from trackingapp.dao.rotator_client import RotatorClient
from trackingapp.service.coordinate_transform_service import CoordinateTransformService


@pytest.fixture(scope="session")
def client():
    return RotatorClient()


@pytest.fixture(scope="session")  # Explicitly set the loop scope
def fastapi_container():
    print("Starting fastapi_container fixture...")  # Debug print
    compose = DockerCompose(".", services=["hamlib"])
    compose.start()
    print("Container started.")
    time.sleep(5)
    yield
    compose.stop()


@pytest.fixture(scope="session")
def coordinates():
    return CoordinateTransformService(37.98, 23.76, 131)


# @pytest.mark.skip(reason="Requires a rotator device.")
@pytest.mark.asyncio
async def test_example(client, coordinates):
    await client.execute(0, 0)
    await client.execute(130, 10)
