from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
from src.domain.auth.repositories import UserRepository
from src.domain.errors import ValidationError
from src.infrastructure.auth.services.hasher import Hasher
from .dtos import RegisterUserRequestDto, RegisterUserResponseDto


class RegisterUser:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, data: RegisterUserRequestDto) -> RegisterUserResponseDto:
        existing_user = await self._user_repo.get_by_email(Email(data.email))
        if existing_user:
            raise ValidationError("Email already registered")

        user = User(
            email=Email(data.email),
            password_hash=Hasher.get_password_hash(data.password),
            full_name=data.full_name
        )
        await self._user_repo.add(user)

        return RegisterUserResponseDto(
            id=user.id,
            email=str(user.email),
            full_name=user.full_name,
            is_active=user.is_active
        )
