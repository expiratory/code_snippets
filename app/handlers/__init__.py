from fastapi import FastAPI


def register_handlers(app: FastAPI) -> None:
    from . import snippet as snippet_handlers
    from . import tag as tag_handlers

    snippet_handlers.attach(app)
    tag_handlers.attach(app)
