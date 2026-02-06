from src.domain.auth.value_objects import Email
from src.domain.auth.repositories import UserRepository
from src.domain.errors import UnauthorizedError
from src.infrastructure.auth.services.hasher import Hasher
from src.infrastructure.auth.services.jwt import JWTService
from .dtos import LoginUserRequestDto, LoginUserResponseDto


class LoginUser:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, data: LoginUserRequestDto) -> LoginUserResponseDto:
        user = await self._user_repo.get_by_email(Email(data.email))
        if not user or not Hasher.verify_password(
                data.password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        if not user.is_active:
            raise UnauthorizedError("User account is deactivated")

        payload = {"sub": str(user.id)}
        access_token = JWTService.create_token(
            data=payload, token_type="access")
        refresh_token = JWTService.create_token(
            data=payload, token_type="refresh")

        return LoginUserResponseDto(
            access_token=access_token,
            refresh_token=refresh_token
        )
