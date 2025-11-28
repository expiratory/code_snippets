import asyncio
import json
import logging

from app.mq import get_connection
from app.redis import get_redis
from app.services.code_runner import CodeRunnerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_message(message, code_runner_service: CodeRunnerService):
    async with message.process():
        body = json.loads(message.body)
        data = body.get("data")
        task_id = data.get("task_id")
        code = data.get("code")
        language = data.get("language")
        version = data.get("version")

        logger.info(f"Processing task {task_id} for {language} {version}")

        result = await code_runner_service.run_code(code, language, version)

        # Publish result to Redis
        redis_gen = get_redis()
        redis_client = await anext(redis_gen)
        try:
            await redis_client.publish(f"task_results:{task_id}", json.dumps(result))
        finally:
            await redis_client.aclose()


async def main():
    code_runner_service = CodeRunnerService()

    connection = await get_connection()
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("code_execution_tasks", durable=True)

        logger.info("Code Runner Worker started, waiting for messages...")

        async for message in queue:
            await process_message(message, code_runner_service)


if __name__ == "__main__":
    asyncio.run(main())
