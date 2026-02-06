from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
from src.infrastructure.auth.models import UserORM


class UserMapper:
    @staticmethod
    def to_domain(orm_user: UserORM) -> User:
        return User(
            email=Email(orm_user.email),
            password_hash=orm_user.password_hash,
            full_name=orm_user.full_name,
            is_active=orm_user.is_active,
            id=orm_user.id
        )

    @staticmethod
    def to_orm(user: User) -> UserORM:
        return UserORM(
            id=user.id,
            email=user.email.value,
            password_hash=user.password_hash,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
