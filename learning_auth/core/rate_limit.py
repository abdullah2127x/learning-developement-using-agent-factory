from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

# # Apply to routes
# @router.post("/login")
# @limiter.limit("5/minute")           # 5 attempts per minute per IP
# async def login_for_access_token():
#     pass