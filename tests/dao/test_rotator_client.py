import time

import pytest
from testcontainers.compose import DockerCompose

from trackingapp.dao.rotator_client import RotatorClient


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


@pytest.mark.skip(reason="Requires a rotator device.")
def test_example(client, fastapi_container):
    client.execute(0, 0)
    client.execute(130, 10)
