import uuid

from jose import JWTError

from src.application.use_cases.auth.login.dtos import LoginUserResponseDto, UserResponseDto
from src.domain.auth.repositories import UserRepository
from src.domain.errors import UnauthorizedError
from src.infrastructure.auth.services.jwt import JWTService

from .dtos import RefreshTokenRequestDto


class RefreshToken:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, data: RefreshTokenRequestDto) -> LoginUserResponseDto:
        try:
            payload = JWTService.decode_token(data.refresh_token)
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise UnauthorizedError("Invalid refresh token")

            user = await self._user_repo.get_by_id(uuid.UUID(user_id))
            if not user or not user.is_active:
                raise UnauthorizedError("User not found or inactive")

            new_payload = {"sub": str(user.id)}
            access_token = JWTService.create_token(
                data=new_payload, token_type="access"
            )
            refresh_token = JWTService.create_token(
                data=new_payload, token_type="refresh"
            )

            return LoginUserResponseDto(
                user=UserResponseDto.model_validate(user),
                access_token=access_token,
                refresh_token=refresh_token
            )
        except JWTError:
            raise UnauthorizedError("Invalid refresh token")
