from pydantic import BaseModel, ConfigDict, field_validator


class LanguageBase(BaseModel):
    name: str


class LanguageCreate(LanguageBase):
    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be empty")
        return v.strip()


class LanguageRead(LanguageBase):
    id: int
    slug: str
    model_config = ConfigDict(from_attributes=True)
