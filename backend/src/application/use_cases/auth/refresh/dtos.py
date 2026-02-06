from pydantic import BaseModel, EmailStr

class RefreshTokenRequestDto(BaseModel):
    refresh_token: str
