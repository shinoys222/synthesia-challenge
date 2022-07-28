import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class RateLimitExceededException(Exception):
    """
    Exception class used to indicate when a request exceeds  RateLimit
    """

    pass


class APIClient:
    """
    Base API Client used to call external API Requests.
    """

    def __init__(
        self,
        base_url: str,
        num_retries: int = 0,
        rate_limit_enabled: bool = False,
        rate_limit_per_minute: int = 0,
        timeout_seconds: float = 0,
    ) -> None:
        self.transport = httpx.AsyncHTTPTransport(retries=num_retries)
        self._client = None
        self.base_url = base_url
        self.rate_limit_enabled = rate_limit_enabled
        self.rate_limit_per_minute = rate_limit_per_minute
        self.timeout_seconds = timeout_seconds
        self.last_req_minute = datetime.min
        self.req_count = 0

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.stop()

    async def start(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        )

    async def stop(self):
        await self._client.aclose()
        self._client = None

    async def apply_rate_limit(self, start_time: datetime):
        """
        Applies the rate limit logic and keeps track of current request count
            and request time.
        If ratelimiting is not enabled returns without exception.
        If ratelimiting is enabled and the request falls under the limit,
            returns without exception
        If ratelimiting is enabled and the request falls over the limit,
            raises RateLimitExceededException
        """
        if not self.rate_limit_enabled:
            return
        diff_seconds = (start_time - self.last_req_minute).total_seconds()
        logger.info(
            f"Ratelimit - enabled:{self.rate_limit_enabled}, rate_limit_per_minute:{self.rate_limit_per_minute},"
            f"seconds: {diff_seconds}, req_count:{self.req_count}"
        )
        if diff_seconds > 60:
            # If the time difference between 2 requests is greater than a minute
            # we update the last_req_minute and the req_count
            self.last_req_minute = start_time.replace(second=0)
            self.req_count = 1
            return
        elif self.req_count < self.rate_limit_per_minute:
            # If the time difference between 2 requests is less than a minute
            # we increase the req_count by 1
            self.req_count += 1
            return
        raise RateLimitExceededException

    async def request(
        self,
        url: str,
        method: str,
        headers: dict = {},
        params: dict = {},
        *args,
        **kwargs,
    ):
        """
        Calls upstream request using the httpx client.
        If ratelimiting is not enabled returns the upstream response.
        If ratelimiting is enabled, raises RateLimitExceededException
        """
        await self.apply_rate_limit(datetime.utcnow())
        return await self._client.request(
            "GET",
            url,
            params=params,
            headers=headers,
            *args,
            **kwargs,
        )
