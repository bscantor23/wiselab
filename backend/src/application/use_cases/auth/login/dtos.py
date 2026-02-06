from pydantic import BaseModel, EmailStr


class LoginUserRequestDto(BaseModel):
    email: EmailStr
    password: str


class LoginUserResponseDto(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
