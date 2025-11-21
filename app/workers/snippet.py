import asyncio
import json
import logging

from app.enums.snippet import SnippetEventEnum
from app.mq import get_connection
from app.services.search import SearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_message(message, search_service: SearchService):
    async with message.process():
        data = json.loads(message.body)
        event = data.get("event")
        payload = data.get("data")

        logger.info(f"Received event: {event}")

        if event in (SnippetEventEnum.CREATED, SnippetEventEnum.UPDATED):
            await search_service.index_snippet(
                snippet_id=payload["id"],
                title=payload["title"],
                code=payload["code"],
                language=payload["language"],
            )
        elif event == SnippetEventEnum.DELETED:
            await search_service.delete_snippet(snippet_id=payload["id"])


async def main():
    search_service = SearchService()

    for _ in range(30):
        try:
            await search_service.create_index()
            break
        except Exception as e:
            logger.warning(f"Waiting for Elasticsearch... {e}")
            await asyncio.sleep(1)
    else:
        logger.error("Could not connect to Elasticsearch after 30 seconds")
        return

    connection = await get_connection()
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("snippet_events", durable=True)

        logger.info("Worker started, waiting for messages...")

        async for message in queue:
            await process_message(message, search_service)


if __name__ == "__main__":
    asyncio.run(main())
