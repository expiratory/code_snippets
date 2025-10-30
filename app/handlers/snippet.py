from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors.snippet import SnippetNotFoundError


def attach(app: FastAPI) -> None:
    @app.exception_handler(SnippetNotFoundError)
    async def snippet_not_found_handler(request: Request, exc: SnippetNotFoundError):
        return JSONResponse(status_code=404, content={"detail": "Snippet not found"})
