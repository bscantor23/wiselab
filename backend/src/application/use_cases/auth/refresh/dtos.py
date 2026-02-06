from pydantic import BaseModel


class RefreshTokenRequestDto(BaseModel):
    refresh_token: str
