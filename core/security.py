from datetime import datetime, timedelta
from jose import jwt, JWTError

from core.config import settings


ALGORITHM = "HS256"


def verify_access_password(password: str) -> bool:
    return password == settings.APP_ACCESS_PASSWORD


def create_access_token() -> str:
    expire = datetime.utcnow() + timedelta(
        hours=settings.TOKEN_EXPIRE_HOURS
    )

    payload = {
        "type": "access",
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_token(token: str) -> bool:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload.get("type") == "access"

    except JWTError:
        return False