import taskiq_fastapi
from taskiq import TaskiqScheduler
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend
from app.core.config import settings

broker_taskiq = AioPikaBroker(
    url=settings.RABBITMQ_URL,
).with_result_backend(
    RedisAsyncResultBackend(
        redis_url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    )
)

taskiq_fastapi.init(broker_taskiq, "app.configuration.server:app")

