import json

import aio_pika

from app.config import settings

RABBITMQ_URL = settings.RABBITMQ_URL


async def get_connection():
    return await aio_pika.connect_robust(RABBITMQ_URL)


async def publish_event(queue_name: str, event_type: str, data: dict):
    connection = await get_connection()
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)

        message = {"event": event_type, "data": data}

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=queue.name,
        )
