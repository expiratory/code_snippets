from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import engine
from app.handlers import register_handlers
from app.limiter import limiter
from app.views.auth import router as auth_router
from app.views.code_runner import router as code_runner_router
from app.views.language import router as language_router
from app.views.snippet import router as snippet_router
from app.views.tag import router as tag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=settings.SESSION_MIDDLEWARE_HTTPS_ONLY,
)

register_handlers(app)

app.include_router(auth_router)
app.include_router(snippet_router)
app.include_router(tag_router)
app.include_router(language_router)
app.include_router(code_runner_router)
