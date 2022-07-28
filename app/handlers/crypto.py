import asyncio
import logging
from typing import Optional
from pydantic import AnyHttpUrl
from datetime import timedelta
from httpx import ConnectTimeout
from app import settings

from app.clients.crypto import client as crypto_client
from app.clients import RateLimitExceededException, APIClient
from app.clients.redis_queue import scheduler as rq_scheduler


logger = logging.getLogger(__name__)


async def sign_message(
    message: str, callback_url: Optional[AnyHttpUrl] = None, attempt_count: int = 0
):
    """
    Sign message calls the upstream crypto service sign endpoint.
    If the upstream endpoint returns 200, then it returns signed data
    If it fails and callback is enabled and the retry attempt is less than specified value,
        it enqueues a job/task to sign the message again using rq scheduler.
    """
    try:
        response = await crypto_client.sign_message(message)
        # If the reponse code is 200, return signed message from response body
        if response.status_code == 200:
            return response.content.decode("utf-8"), True
        logger.info(
            f"Upstream response failed - status_code: {response.status_code}, content: {response.content}"
        )
    except RateLimitExceededException:
        logger.info("Upstream rate limit exceeded")
    except ConnectTimeout:
        logger.info("Upstream request timedout")
    except Exception as e:
        logger.error(f"API Request Failed - {str(e)} ")
        logger.exception(e)
    if (
        callback_url
        and settings.callback.enabled
        and attempt_count < settings.callback.max_upstream_attempts
    ):
        logger.info(
            f"Scheduling upstream request to be retried in {settings.callback.enqeueue_delay_seconds}"
        )
        rq_scheduler.enqueue_in(
            timedelta(seconds=settings.callback.enqeueue_delay_seconds),
            sign_message_and_notify_event,
            message,
            callback_url,
            attempt_count + 1,
        )
    return None, False


async def sign_message_and_notify_callback(
    message: str, callback_url: Optional[AnyHttpUrl], attempt_count: int = 0
):
    logger.info(
        f"Signing message:{message}, callback_url:{callback_url}, attempt_count:{attempt_count}"
    )
    response, success = await sign_message(message, callback_url, attempt_count)
    if not success:
        return
    # notify the callback url, that the message is successfully signed
    params = {"success": success, "data": response}
    logger.info(
        f"Notifying callback, message:{message}, callback_url:{callback_url}, attempt_count:{attempt_count}"
    )
    try:
        base_url = f"{callback_url.scheme}://{callback_url.host}"
        if callback_url.port:
            base_url = base_url + f":{callback_url.port}"
        async with APIClient(
            base_url=base_url,
            num_retries=settings.callback.max_retry_count,
            rate_limit_enabled=False,
            timeout_seconds=settings.callback.timeout_seconds,
        ) as api_client:
            await api_client.request(url=callback_url.path, method="POST", params=params)
    except Exception as e:
        logger.error(f"Callback API Request Failed - {str(e)} ")
        logger.exception(e)


def sign_message_and_notify_event(
    message: str, callback_url: Optional[AnyHttpUrl], attempt_count: int = 0
):
    """
    Acts on redis queue event/message to sign and notify callback url
    """
    try:
        logger.info(
            f"Recieved rq event message:{message}, callback_url:{callback_url}, attempt_count:{attempt_count}"
        )
        coro = sign_message_and_notify_callback(message, callback_url, attempt_count)
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(coro)
    except Exception as e:
        logger.exception(e)
