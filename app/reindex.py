import asyncio
import logging

from app.db import SessionLocal
from app.repos.snippet import Snippet
from app.services.search import SearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reindex_all():
    logger.info("Starting re-indexing process...")

    search_service = SearchService()

    await search_service.create_index()

    async with SessionLocal() as session:
        snippets = await Snippet.get_all(session)
        logger.info(f"Found {len(snippets)} snippets in database.")

        for snippet in snippets:
            try:
                await search_service.index_snippet(
                    snippet_id=snippet.id,
                    title=snippet.title,
                    code=snippet.code,
                    language=snippet.language,
                )
                logger.info(f"Indexed snippet {snippet.id}")
            except Exception as e:
                logger.error(f"Failed to index snippet {snippet.id}: {e}")

    await search_service.close()
    logger.info("Re-indexing completed.")


if __name__ == "__main__":
    asyncio.run(reindex_all())
