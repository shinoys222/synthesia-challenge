import pytest
from pytest_httpx import HTTPXMock

from app import settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    (
        "upstream_status_code",
        "upstream_data",
        "expected_success",
        "expected_data",
        "expected_status_code",
    ),
    [
        (200, "signed_data", True, "signed_data", 200),
        (502, "Service Degradation", False, None, 200),
    ],
    ids=[
        "upstream_success",
        "upstream_failure",
    ],
)
async def test_sign_message_no_callback(
    httpx_mock: HTTPXMock,
    upstream_status_code,
    upstream_data,
    expected_success,
    expected_data,
    expected_status_code,
    client,
):
    httpx_mock.add_response(
        method="GET",
        url=f"{settings.crypto_client.base_url}/crypto/sign?message=test",
        status_code=upstream_status_code,
        content=upstream_data.encode("utf-8"),
    )
    response = client.get("/crypto/sign?message=test")

    assert response.status_code == expected_status_code
    assert response.json() == {"success": expected_success, "data": expected_data}
