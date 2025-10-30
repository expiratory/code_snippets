from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.db import engine
from app.handlers import register_handlers
from app.views.snippet import router as snippet_router
from app.views.tag import router as tag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

register_handlers(app)

app.include_router(snippet_router)
app.include_router(tag_router)
