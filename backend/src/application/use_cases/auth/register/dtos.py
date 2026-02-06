from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID


class RegisterUserRequestDto(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v


class RegisterUserResponseDto(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        if hasattr(v, "value"):
            return v.value
        return v

    class Config:
        from_attributes = True
