from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors.language import LanguageNotFoundError


def attach(app: FastAPI) -> None:
    @app.exception_handler(LanguageNotFoundError)
    async def language_not_found_handler(request: Request, exc: LanguageNotFoundError):
        return JSONResponse(status_code=404, content={"detail": "Language not found"})
