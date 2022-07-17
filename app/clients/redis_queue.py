from redis import Redis
from rq_scheduler import Scheduler

from app import settings

scheduler = Scheduler(
    settings.redis_queue.name, connection=Redis.from_url(settings.redis_queue.url)
)
