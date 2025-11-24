from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.errors.language import LanguageNotFoundError
from app.handlers.language import attach as attach_language_handlers


def test_language_not_found_handler():
    app = FastAPI()
    attach_language_handlers(app)

    @app.get("/error")
    def error_endpoint():
        raise LanguageNotFoundError()

    client = TestClient(app)
    response = client.get("/error")
    assert response.status_code == 404
    assert response.json() == {"detail": "Language not found"}
