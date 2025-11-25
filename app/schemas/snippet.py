from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.language import LanguageRead
from app.schemas.tag import TagRead


class SnippetBase(BaseModel):
    title: str
    code: str


class SnippetCreate(SnippetBase):
    language_id: int
    tags: List[str] = []

    @field_validator("code")
    @classmethod
    def validate_code_length(cls, v: str) -> str:
        if len(v) > 10000:
            raise ValueError("Code snippet must be 10000 characters or less")
        return v


class SnippetUpdate(SnippetBase):
    language_id: Optional[int] = None
    tags: Optional[List[str]] = None

    @field_validator("code")
    @classmethod
    def validate_code_length(cls, v: str) -> str:
        if len(v.splitlines()) > 100:
            raise ValueError("Code snippet must be 100 lines or less")
        return v


class SnippetRead(SnippetBase):
    id: int
    language: Optional[LanguageRead] = None
    tags: List[TagRead] = []
    model_config = ConfigDict(from_attributes=True)
