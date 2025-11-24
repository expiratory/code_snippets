from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_current_user,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.config import settings
from app.errors.auth import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotFoundError,
)


def test_verify_password():
    password = "Password123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_create_access_token():
    data = {"sub": "1", "email": "test@example.com"}
    token = create_access_token(data)
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "1"
    assert decoded["email"] == "test@example.com"
    assert decoded["type"] == "access"


def test_create_refresh_token():
    data = {"sub": "1", "email": "test@example.com"}
    token = create_refresh_token(data)
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "1"
    assert decoded["type"] == "refresh"


def test_verify_refresh_token_valid():
    data = {"sub": "1", "email": "test@example.com"}
    token = create_refresh_token(data)
    payload = verify_refresh_token(token)
    assert payload is not None
    assert payload["sub"] == "1"


def test_verify_refresh_token_invalid_type():
    data = {"sub": "1", "email": "test@example.com"}
    token = create_access_token(data)
    payload = verify_refresh_token(token)
    assert payload is None


def test_verify_refresh_token_invalid_jwt():
    payload = verify_refresh_token("invalid.token")
    assert payload is None


def test_decode_access_token_valid():
    data = {"sub": "1", "email": "test@example.com"}
    token = create_access_token(data)
    token_data = decode_access_token(token)
    assert token_data.user_id == 1
    assert token_data.email == "test@example.com"


def test_decode_access_token_invalid():
    with pytest.raises(InvalidTokenError):
        decode_access_token("invalid.token")


def test_decode_access_token_missing_claims():
    token = jwt.encode({"sub": 1}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


@pytest.mark.asyncio
async def test_authenticate_user_success():
    mock_session = AsyncMock()
    mock_user = MagicMock()
    mock_user.hashed_password = hash_password("Password123!")

    with patch("app.auth.User") as mock_user_cls:
        mock_user_cls.get_by_email = AsyncMock(return_value=mock_user)

        user = await authenticate_user(mock_session, "test@example.com", "Password123!")
        assert user == mock_user


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    mock_session = AsyncMock()

    with patch("app.auth.User") as mock_user_cls:
        mock_user_cls.get_by_email = AsyncMock(side_effect=UserNotFoundError)

        with pytest.raises(InvalidCredentialsError):
            await authenticate_user(mock_session, "test@example.com", "Password123!")


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    mock_session = AsyncMock()
    mock_user = MagicMock()
    mock_user.hashed_password = hash_password("Password123!")

    with patch("app.auth.User") as mock_user_cls:
        mock_user_cls.get_by_email = AsyncMock(return_value=mock_user)

        with pytest.raises(InvalidCredentialsError):
            await authenticate_user(mock_session, "test@example.com", "WrongPassword")


@pytest.mark.asyncio
async def test_get_current_user_success():
    mock_session = AsyncMock()
    mock_user = MagicMock()
    mock_user.is_active = True

    token = create_access_token({"sub": "1", "email": "test@example.com"})

    with patch("app.auth.User") as mock_user_cls:
        mock_user_cls.get_by_id = AsyncMock(return_value=mock_user)

        user = await get_current_user(token, mock_session)
        assert user == mock_user


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    mock_session = AsyncMock()
    with pytest.raises(Exception):
        await get_current_user("invalid", mock_session)


@pytest.mark.asyncio
async def test_get_current_user_not_found():
    mock_session = AsyncMock()
    token = create_access_token({"sub": 1, "email": "test@example.com"})

    with patch("app.auth.User") as mock_user_cls:
        mock_user_cls.get_by_id = AsyncMock(side_effect=UserNotFoundError)

        with pytest.raises(Exception):
            await get_current_user(token, mock_session)


@pytest.mark.asyncio
async def test_get_current_user_inactive():
    mock_session = AsyncMock()
    mock_user = MagicMock()
    mock_user.is_active = False

    token = create_access_token({"sub": "1", "email": "test@example.com"})

    with patch("app.auth.User") as mock_user_cls:
        mock_user_cls.get_by_id = AsyncMock(return_value=mock_user)

        with pytest.raises(Exception) as exc:
            await get_current_user(token, mock_session)
        assert exc.value.status_code == 400
