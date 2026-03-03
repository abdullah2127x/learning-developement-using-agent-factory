"""
Rate limiting utilities for the FastAPI application.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address


# Create a single limiter instance to be used throughout the application
limiter = Limiter(key_func=get_remote_address)