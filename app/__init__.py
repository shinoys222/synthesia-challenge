from pydantic import BaseSettings


class CryptoClientSettings(BaseSettings):
    base_url: str = "https://hiring.api.synthesia.io"
    api_key: str = "api_key"
    timeout_seconds: float = 1.0
    rate_limit_enabled: bool = True
    rate_limit_req_per_minute: int = 5

    class Config:
        env_prefix = "crypto_client_"


class CallbackSettings(BaseSettings):
    enabled: bool = True
    # Max number of attempts to call upstream crypto request
    max_upstream_attempts: int = 10
    # Max retry count to notify caller
    max_retry_count: int = 1
    # Delay to enqueue a new upstream crypto request after failure
    enqeueue_delay_seconds: int = 20
    timeout_seconds: float = 1.0

    class Config:
        env_prefix = "callback_"


class RedisQueueSettings(BaseSettings):
    name: str = "callback_queue"
    url: str = "redis://redis:6379/0"

    class Config:
        env_prefix = "redis_queue_"


class Settings(BaseSettings):
    crypto_client: CryptoClientSettings = CryptoClientSettings()
    redis_queue: RedisQueueSettings = RedisQueueSettings()
    callback: CallbackSettings = CallbackSettings()
    debug: bool = False


settings = Settings()
