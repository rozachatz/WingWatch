import time

import pytest
from testcontainers.compose import DockerCompose
from app.dao.AdsbClient import AdsbClient

@pytest.fixture(scope="session")
def client():
    return AdsbClient()


@pytest.fixture(scope="session")  # Explicitly set the loop scope
def fastapi_container():
    print("Starting fastapi_container fixture...")  # Debug print
    compose = DockerCompose(".", services=["dump1090"])
    compose.start()
    print("Container started.")
    time.sleep(10)
    yield
    compose.stop()


def test_example(client, fastapi_container):
    response = client.getAdsb()
    assert response.status_code == 200
