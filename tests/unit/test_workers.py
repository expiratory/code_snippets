import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.enums.snippet import SnippetEventEnum
from app.workers.snippet import main, process_message


@pytest.mark.asyncio
async def test_process_message_created():
    mock_search_service = AsyncMock()
    mock_message = MagicMock()
    mock_message.process.return_value.__aenter__.return_value = None
    mock_message.process.return_value.__aexit__.return_value = None

    payload = {"id": 1, "title": "Title", "code": "Code", "language": "Python"}
    mock_message.body = json.dumps(
        {"event": SnippetEventEnum.CREATED.value, "data": payload}
    )

    await process_message(mock_message, mock_search_service)

    mock_search_service.index_snippet.assert_called_with(
        snippet_id=1, title="Title", code="Code", language="Python"
    )


@pytest.mark.asyncio
async def test_process_message_deleted():
    mock_search_service = AsyncMock()
    mock_message = MagicMock()
    mock_message.process.return_value.__aenter__.return_value = None
    mock_message.process.return_value.__aexit__.return_value = None

    payload = {"id": 1}
    mock_message.body = json.dumps(
        {"event": SnippetEventEnum.DELETED.value, "data": payload}
    )

    await process_message(mock_message, mock_search_service)

    mock_search_service.delete_snippet.assert_called_with(snippet_id=1)


@pytest.mark.asyncio
async def test_worker_main():
    with (
        patch("app.workers.snippet.SearchService") as mock_search_cls,
        patch("app.workers.snippet.get_connection") as mock_get_conn,
    ):
        mock_search = AsyncMock()
        mock_search_cls.return_value = mock_search

        mock_conn = AsyncMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.__aenter__.return_value = mock_conn
        mock_conn.__aexit__.return_value = None

        mock_channel = AsyncMock()
        mock_conn.channel.return_value = mock_channel

        # Mock queue iterator
        mock_queue = AsyncMock()
        mock_queue.__aiter__.return_value = [MagicMock()]
        mock_channel.declare_queue.return_value = mock_queue

        # Mock process_message to avoid actual processing logic in main test
        with patch(
            "app.workers.snippet.process_message", new_callable=AsyncMock
        ) as mock_process:
            await main()

            mock_search.create_index.assert_called()
            mock_channel.declare_queue.assert_called_with(
                "snippet_events", durable=True
            )
            mock_process.assert_called()


@pytest.mark.asyncio
async def test_worker_main_retry():
    with (
        patch("app.workers.snippet.SearchService") as mock_search_cls,
        patch("app.workers.snippet.get_connection") as mock_get_conn,
        patch(
            "app.workers.snippet.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep,
    ):
        mock_search = AsyncMock()
        mock_search_cls.return_value = mock_search

        # Fail first time, succeed second time
        mock_search.create_index.side_effect = [Exception("Fail"), None]

        mock_conn = AsyncMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.__aenter__.return_value = mock_conn
        mock_conn.__aexit__.return_value = None

        mock_channel = AsyncMock()
        mock_conn.channel.return_value = mock_channel

        mock_queue = AsyncMock()
        mock_queue.__aiter__.return_value = []
        mock_channel.declare_queue.return_value = mock_queue

        await main()

        assert mock_search.create_index.call_count == 2
        mock_sleep.assert_called_once_with(1)
