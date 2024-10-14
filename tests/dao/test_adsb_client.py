import time

import pytest
from testcontainers.compose import DockerCompose

from app.dao.adsb_client import AdsbClient


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


@pytest.mark.skip(reason="Requires a RTL SDR device.")
def test_example(client, fastapi_container):
    response = client.getAdsb()
    assert response.status_code == 200
