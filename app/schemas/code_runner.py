from pydantic import BaseModel, Field

from app.enums.language import RunLanguage


class CodeRunRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=10000)
    language: str = Field(..., pattern=f"^({'|'.join(RunLanguage.get_languages())})$")


class CodeRunResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
