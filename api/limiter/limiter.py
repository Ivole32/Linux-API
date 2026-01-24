from slowapi import Limiter
from slowapi.util import get_remote_address

from api.config.config import API_RATE_LIMIT_ENABLED, API_DEFAULT_RATE_LIMITS

limiter = Limiter(enabled=API_RATE_LIMIT_ENABLED, default_limits=API_DEFAULT_RATE_LIMITS, key_func=get_remote_address)