import nest_asyncio
import asyncio
import pytest
from fastapi.testclient import TestClient
from main import api


def pytest_sessionstart(session):
    nest_asyncio.apply()


@pytest.fixture(scope="module")
def event_loop():
    yield asyncio.get_event_loop()


@pytest.fixture(scope="function")
def client():
    from app import settings

    settings.debug = True
    app = api()
    with TestClient(app) as _client:
        yield _client
