from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors.tag import TagNotFoundError


def attach(app: FastAPI) -> None:
    @app.exception_handler(TagNotFoundError)
    async def tag_not_found_handler(request: Request, exc: TagNotFoundError):
        return JSONResponse(status_code=404, content={"detail": "Tag not found"})
