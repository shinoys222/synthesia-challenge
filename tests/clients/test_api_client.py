import pytest
from datetime import datetime
from pytest_httpx import HTTPXMock

from app.clients import APIClient, RateLimitExceededException


pytestmark = pytest.mark.asyncio


async def test_api_client_rate_limit_success(
    httpx_mock: HTTPXMock,
    client,
):
    client = APIClient(
        base_url="http://test", rate_limit_enabled=True, rate_limit_per_minute=10
    )
    client.req_count = 1
    client.last_req_minute = datetime.utcnow().replace(second=0)
    await client.start()
    httpx_mock.add_response(
        method="GET",
        url="http://test/test",
        status_code=200,
        json={},
    )

    response = await client.request(url="/test", method="GET")
    response.status_code == 200
    assert response.json() == {}


async def test_api_client_rate_limit_exceeded(
    httpx_mock: HTTPXMock,
    client,
):
    client = APIClient(
        base_url="http://test", rate_limit_enabled=True, rate_limit_per_minute=10
    )
    client.req_count = 10
    client.last_req_minute = datetime.utcnow().replace(second=0)
    await client.start()

    with pytest.raises(RateLimitExceededException):
        await client.request(url="/test", method="GET")
