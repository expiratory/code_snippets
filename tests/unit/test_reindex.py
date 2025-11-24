from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.reindex import reindex_all


@pytest.mark.asyncio
async def test_reindex_all():
    with (
        patch("app.reindex.SearchService") as mock_search_cls,
        patch("app.reindex.SessionLocal") as mock_session_cls,
        patch("app.reindex.Snippet") as mock_snippet_cls,
    ):
        mock_search = AsyncMock()
        mock_search_cls.return_value = mock_search

        mock_session = AsyncMock()
        mock_session_cls.return_value = mock_session
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        snippet1 = MagicMock(id=1, title="T1", code="C1", language="L1")
        snippet2 = MagicMock(id=2, title="T2", code="C2", language="L2")

        async def mock_get_all(*args, **kwargs):
            return [snippet1, snippet2]

        mock_snippet_cls.get_all.side_effect = mock_get_all

        await reindex_all()

        mock_search.create_index.assert_called_once()
        assert mock_search.index_snippet.call_count == 2
        mock_search.close.assert_called_once()
