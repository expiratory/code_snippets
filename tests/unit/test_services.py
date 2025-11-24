from unittest.mock import AsyncMock, patch

import pytest

from app.services.search import SearchService


@pytest.mark.asyncio
async def test_search_service_create_index():
    with patch("app.services.search.AsyncElasticsearch") as mock_es_cls:
        mock_es = AsyncMock()
        mock_es_cls.return_value = mock_es

        service = SearchService()

        # Test index exists
        mock_es.indices.exists.return_value = True
        await service.create_index()
        mock_es.indices.create.assert_not_called()

        # Test index does not exist
        mock_es.indices.exists.return_value = False
        await service.create_index()
        mock_es.indices.create.assert_called_once()

        await service.close()


@pytest.mark.asyncio
async def test_search_service_index_snippet():
    with patch("app.services.search.AsyncElasticsearch") as mock_es_cls:
        mock_es = AsyncMock()
        mock_es_cls.return_value = mock_es

        service = SearchService()
        await service.index_snippet(1, "Title", "Code", "Python")

        mock_es.index.assert_called_with(
            index="snippets",
            id="1",
            document={
                "id": 1,
                "title": "Title",
                "code": "Code",
                "language": "Python",
            },
        )
        await service.close()


@pytest.mark.asyncio
async def test_search_service_delete_snippet():
    with patch("app.services.search.AsyncElasticsearch") as mock_es_cls:
        mock_es = AsyncMock()
        mock_es_cls.return_value = mock_es

        service = SearchService()
        await service.delete_snippet(1)

        mock_es.delete.assert_called_with(index="snippets", id="1", ignore=[404])
        await service.close()


@pytest.mark.asyncio
async def test_search_service_search_snippets():
    with patch("app.services.search.AsyncElasticsearch") as mock_es_cls:
        mock_es = AsyncMock()
        mock_es_cls.return_value = mock_es

        service = SearchService()

        # Mock search response
        mock_es.search.return_value = {
            "hits": {
                "hits": [
                    {"_id": "1"},
                    {"_id": "2"},
                ]
            }
        }

        results = await service.search_snippets("query")
        assert results == [1, 2]

        mock_es.search.assert_called_with(
            index="snippets",
            body={
                "query": {
                    "multi_match": {
                        "query": "query",
                        "fields": ["title", "code"],
                        "fuzziness": "AUTO",
                    }
                }
            },
        )
        await service.close()
