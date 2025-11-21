import redis.asyncio as redis

from app.config import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT


async def get_redis():
    client = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()
