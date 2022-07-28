import pytest
import asyncio
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


async def test_api_client_rate_limit_race_conditions(
    client,
):
    rate_limit_per_minute = 5
    total_req_count = 10000

    client = APIClient(
        base_url="http://test", rate_limit_enabled=True, rate_limit_per_minute=rate_limit_per_minute
    )
    client.req_count = 0
    client.last_req_minute = datetime.utcnow().replace(second=0)
    start_time = datetime.utcnow()

    coroutines = [client.apply_rate_limit(start_time) for _ in range(total_req_count)]
    responses = await asyncio.gather(*coroutines, return_exceptions=True)
    failed_count = len([r for r in responses if isinstance(r, RateLimitExceededException)])
    assert failed_count == total_req_count - rate_limit_per_minute
