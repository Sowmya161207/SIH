from typing import Optional

from app.core.security import (
    create_access_token,
    verify_password,
)


# Temporary local users for the hackathon MVP.
# Passwords are stored as Argon2 hashes, never plaintext.
USERS = {
    "operator": {
        "username": "operator",
        "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$67h7KnsZMLNmemPTrhIk7A$9wNJOXPwFC5Wi114MbN0SgJdLHDtAdKQakPrt45r3v4",
        "role": "operator",
    },

    "maintenance": {
        "username": "maintenance",
        "password_hash": "YOUR_MAINTENANCE_HASH",
        "role": "maintenance_engineer",
    },

    "safety": {
        "username": "safety",
        "password_hash": "YOUR_SAFETY_HASH",
        "role": "safety_officer",
    },

    "manager": {
        "username": "manager",
        "password_hash": "YOUR_MANAGER_HASH",
        "role": "manager",
    },
}

def authenticate_user(
    username: str,
    password: str,
) -> Optional[dict]:

    user = USERS.get(username)

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