from abc import abstractmethod
from typing import Optional

from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
from src.domain.repository import Repository


class UserRepository(Repository[User]):
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        pass
