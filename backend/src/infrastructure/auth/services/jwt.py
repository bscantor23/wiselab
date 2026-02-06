import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "5SJ3@Nv715c6")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class JWTService:
    @staticmethod
    def create_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        token_type: str = "access",
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            if token_type == "access":
                expire = datetime.utcnow() + timedelta(
                    minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                )
            else:
                expire = datetime.utcnow() + timedelta(days=7)

        to_encode.update({"exp": expire, "type": token_type})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
