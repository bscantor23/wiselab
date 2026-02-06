from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from uuid import UUID
from typing import Optional


class UserResponseDto(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        if hasattr(v, "value"):
            return str(v.value)
        return str(v)

    model_config = ConfigDict(from_attributes=True)


class LoginUserRequestDto(BaseModel):
    email: EmailStr
    password: str


class LoginUserResponseDto(BaseModel):
    user: UserResponseDto
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
