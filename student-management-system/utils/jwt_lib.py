from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from core.config import settings

# settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


# # if __name__ == "__main__":
# token = create_access_token({"sub": "alice@example.com"})
# print(f"Generated Token: {token}")
# decoded = decode_token(token)
# print(f"Decoded Token: {decoded}")