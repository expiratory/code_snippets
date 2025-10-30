from pydantic import BaseModel, ConfigDict


class SnippetBase(BaseModel):
    title: str
    code: str
    language: str


class SnippetCreate(SnippetBase):
    pass


class SnippetUpdate(SnippetBase):
    pass


class SnippetRead(SnippetBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
