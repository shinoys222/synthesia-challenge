import logging
from typing import Optional
from pydantic import AnyHttpUrl

from app.handlers import crypto as crypto_handler


logger = logging.getLogger(__name__)


async def sign_message(message: str, callback_url: Optional[AnyHttpUrl] = None):
    logger.info(
        f"Request recieved /crypto/sign message:{message} callback_url: {callback_url}"
    )
    signed_message_data, success = await crypto_handler.sign_message(
        message, callback_url
    )
    return {"success": success, "data": signed_message_data}
