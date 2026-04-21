# # core/jwt.py
# -----------------------Manual JWT handling (no external libraries)-----------------------
# from datetime import datetime, timedelta, timezone
# from typing import Any

# import jwt
# from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError

# from core.config import settings
# from models.user import User

# def create_access_token(subject: str | int) -> str:
#     """Short-lived access token (used in every request)."""
#     expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
#     to_encode = {
#         "sub": str(subject),
#         "exp": expire,
#         "iat": datetime.now(timezone.utc),
#         "type": "access",
#     }
#     return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# def create_refresh_token(subject: str | int) -> str:
#     """Long-lived refresh token (only used to get new access token)."""
#     expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
#     to_encode = {
#         "sub": str(subject),
#         "exp": expire,
#         "iat": datetime.now(timezone.utc),
#         "type": "refresh",
#     }
#     return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
#     """Verify token and enforce type (access or refresh)."""
#     try:
#         print("Verifying token:", token)  # Debugging line
#         payload = jwt.decode(
#             token,
#             settings.jwt_secret,
#             algorithms=[settings.jwt_algorithm]
#         )
#         if(payload):
#             print("Token decoded successfully:", payload)  # Debugging line
#         else:
#             print("Token decoding returned None or empty payload")  # Debugging line



#         print("Decoded token payload:", payload)  # Debugging line
#         if "type" in payload and payload["type"] != token_type:
#             print(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")  # Debugging line
#             raise ValueError(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
#         print("Token is valid and type matches.")  # Debugging line
#         return payload
#     except ExpiredSignatureError:
#         raise ValueError("Token has expired")
#     except (InvalidTokenError, PyJWTError) as e:
#         print(f"Token verification error: {str(e)}")  # Debugging line
#         raise ValueError("Invalid token", str(e))

# ================Using better authentication library on the frontend so setting the backend here accordingly( using the EdDSA and JWKS)=========================
from jwt import PyJWKClient
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
import jwt

JWKS_URL = "http://localhost:3000/api/auth/jwks"

jwks_client = PyJWKClient(JWKS_URL)

def verify_token(token: str) -> dict:
    try:
        print("Verifying token:", token)
        print("JWKS URL:", jwks_client)
        # 🔑 Get public key from Better Auth
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        print("Obtained signing key:", signing_key) 

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA"],   # ✅ IMPORTANT
            audience="http://localhost:3000",  # must match token
        )

        print("Decoded payload:", payload)
        return payload

    except ExpiredSignatureError:
        print("Token expired error")
        raise ValueError("Token expired")

    except Exception as e:
        print("Verification error:", str(e))
        raise ValueError("Invalid token")
