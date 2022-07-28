import typer
import asyncio
import logging
import sys
from rq import Connection, SimpleWorker
from redis import Redis

from app import settings
from app.fastapi_app import app as fastapi_app
from app.clients.crypto import client as crypto_client

logger = logging.getLogger(__name__)
typer_app = typer.Typer()


def api():
    setup_logging()
    return fastapi_app


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    stdout_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)


@typer_app.command()
def start_worker():
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(crypto_client.start())
    setup_logging()
    logger.info("Starting Redis Queue Workers")
    with Connection(connection=Redis.from_url(settings.redis_queue.url)):
        worker = SimpleWorker(settings.redis_queue.name)
        worker.work()


if __name__ == "__main__":
    typer_app()
