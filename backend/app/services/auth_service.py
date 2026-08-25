from typing import Optional

from app.core.security import (
    create_access_token,
    verify_password,
)
from app.db.database import get_user_by_username


def authenticate_user(
    username: str,
    password: str,
) -> Optional[dict]:

    user = get_user_by_username(username)

    if not user:
        return None

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return None

    return user


def login_user(
    username: str,
    password: str,
) -> Optional[dict]:

    user = authenticate_user(
        username,
        password,
    )

    if not user:
        return None

    token = create_access_token(
        {
            "sub": user["username"],
            "role": user["role"],
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role": user["role"],
        },
    }