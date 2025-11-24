from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import NoResultFound

from app.errors.auth import UserNotFoundError
from app.errors.snippet import SnippetNotFoundError
from app.repos.snippet import Snippet
from app.repos.user import User
from app.schemas.snippet import SnippetUpdate


@pytest.mark.asyncio
async def test_snippet_get_by_id_not_found():
    mock_session = AsyncMock()
    mock_session.execute.side_effect = NoResultFound

    with pytest.raises(SnippetNotFoundError):
        await Snippet.get_by_id(mock_session, 1, 1)


@pytest.mark.asyncio
async def test_snippet_update_not_found():
    mock_session = AsyncMock()
    mock_session.execute.side_effect = NoResultFound

    with pytest.raises(SnippetNotFoundError):
        await Snippet.update(mock_session, 1, SnippetUpdate(title="New", code="New"), 1)


@pytest.mark.asyncio
async def test_snippet_delete_not_found():
    mock_session = AsyncMock()
    mock_session.execute.side_effect = NoResultFound

    with pytest.raises(SnippetNotFoundError):
        await Snippet.delete(mock_session, 1, 1)


@pytest.mark.asyncio
async def test_user_get_by_id_not_found():
    mock_session = AsyncMock()
    mock_session.execute.side_effect = NoResultFound

    with pytest.raises(UserNotFoundError):
        await User.get_by_id(mock_session, 1)


@pytest.mark.asyncio
async def test_user_get_by_email_not_found():
    mock_session = AsyncMock()
    mock_session.execute.side_effect = NoResultFound

    user = await User.get_by_email(mock_session, "test@example.com")
    assert user is None
