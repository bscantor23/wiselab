import re

from src.domain.errors import ValidationError


class Email:
    def __init__(self, value: str):
        if not self._validate(value):
            raise ValidationError("Invalid email format")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def _validate(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value == other.value
