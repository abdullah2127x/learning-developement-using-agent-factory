
#     # core/security.py
# from argon2 import PasswordHasher as Argon2PasswordHasher  # ← alternative
# from argon2.exceptions import VerifyMismatchError
# from passlib.context import CryptContext
# from passlib.exc import UnknownHashError
# from typing import Literal
# from core.config import settings

# # Bcrypt scheme (deprecated but still available)
# bcrypt_ctx = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto",
#     bcrypt__rounds=settings.bcrypt_rounds,
# )

# argon2_ph = Argon2PasswordHasher(
#     time_cost=settings.argon2_time_cost,
#     memory_cost=settings.argon2_memory_cost,
#     parallelism=8,
# )

# HasherType = Literal["bcrypt", "argon2"]

# def get_password_hash(plain_password: str, hasher: HasherType = "argon2") -> str:
#     """Hash a password using the specified hasher."""
#     if hasher == "argon2":
#         return argon2_ph.hash(plain_password)
#     elif hasher == "bcrypt":
#         return bcrypt_ctx.hash(plain_password)
#     else:
#         raise ValueError(f"Unsupported hasher type: {hasher}")


# def verify_password(plain_password: str, hashed_password: str, hasher: HasherType = "argon2") -> bool:
#     """Verify a password against a hash using the specified hasher."""
#     if hasher == "argon2":
#         try:
#             return argon2_ph.verify(hashed_password, plain_password)
#         except VerifyMismatchError:
#             return False
#     elif hasher == "bcrypt":
#         return bcrypt_ctx.verify(plain_password, hashed_password)
#     raise ValueError(f"Unsupported hasher type: {hasher}")















# core/security.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from typing import Literal
from core.config import settings

# Single, high-security hasher (Argon2id – gold standard in 2026)
argon2_ph = PasswordHasher(
    time_cost=settings.argon2_time_cost,      # iterations
    memory_cost=settings.argon2_memory_cost,  # KiB (100 MiB is excellent)
    parallelism=8,
    hash_len=32,
    salt_len=16,
)

# We keep the type for clarity (even though we only use argon2 now)
HasherType = Literal["argon2"]


def get_password_hash(plain_password: str, hasher: HasherType = "argon2") -> str:
    """Hash a password using Argon2id (memory-hard, GPU-resistant)."""
    if hasher != "argon2":
        raise ValueError("Only argon2 is supported in this project")
    return argon2_ph.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str, hasher: HasherType = "argon2") -> bool:
    """Verify a password against an Argon2id hash."""
    if hasher != "argon2":
        raise ValueError("Only argon2 is supported in this project")
    
    try:
        return argon2_ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False  # Never reveal why it failed (security best practice)