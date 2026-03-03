from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For behind a reverse proxy."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Singleton limiter — import this in any router that needs rate limits
limiter = Limiter(
    key_func=_get_client_ip,
    default_limits=["200/minute"],
    storage_uri="memory://",  # Use "redis://localhost:6379" in production
)

# Pre-defined rate strings — keep limits in one place
AUTH_RATE = "5/minute"      # Login / token endpoints
SIGNUP_RATE = "10/hour"     # Registration
WRITE_RATE = "30/minute"    # POST / PUT / PATCH / DELETE
READ_RATE = "60/minute"     # GET heavy endpoints


def setup_rate_limiter(app: FastAPI) -> None:
    """Register the limiter on the FastAPI app. Call once in main.py."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
