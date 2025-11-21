from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.validators.password import validate_password_strength


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(errors[0])
        return v

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserCreate":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(errors[0])
        return v

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ChangePassword":
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match")
        return self


class GoogleRegister(BaseModel):
    password: str
    confirm_password: str
    registration_token: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(errors[0])
        return v

    @model_validator(mode="after")
    def check_passwords_match(self) -> "GoogleRegister":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    email: str
