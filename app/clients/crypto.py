import logging
from app.clients import APIClient
from app import settings

logger = logging.getLogger(__name__)


class CryptoClient(APIClient):
    def __init__(self, api_key: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        self.sign_endpoint = "/crypto/sign"
        self.verify_endpoint = "/crypto/verify"

    async def sign_message(self, message: str):
        query_params = {"message": message}
        headers = {"Authorization": self.api_key}
        return await self.request(
            url=self.sign_endpoint, method="GET", params=query_params, headers=headers
        )


client = CryptoClient(
    base_url=settings.crypto_client.base_url,
    api_key=settings.crypto_client.api_key,
    timeout_seconds=settings.crypto_client.timeout_seconds,
    num_retries=0,
    rate_limit_enabled=settings.crypto_client.rate_limit_enabled,
    rate_limit_per_minute=settings.crypto_client.rate_limit_req_per_minute,
)
