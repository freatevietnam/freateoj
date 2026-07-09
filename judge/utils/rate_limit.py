from django.conf import settings
from django.core.cache import cache


class EmailRateLimiter:
    """Rate limiter for email APIs using Django cache."""

    def __init__(self, api_type):
        if api_type not in settings.EMAIL_RATE_LIMITS:
            raise ValueError(f'Unknown API type: {api_type}')
        self.api_type = api_type
        self.config = settings.EMAIL_RATE_LIMITS[api_type]

    def _get_cache_key(self, user_id):
        return f'email_rate:{self.api_type}:{user_id}'

    def is_allowed(self, user_id):
        """Check if request is allowed. Returns (allowed: bool, remaining: int)."""
        key = self._get_cache_key(user_id)
        current = cache.get(key, 0)
        
        if current >= self.config['count']:
            return False, 0
        
        # Increment counter
        if current == 0:
            cache.set(key, 1, self.config['window'])
        else:
            cache.incr(key)
        
        return True, self.config['count'] - current - 1

    def get_remaining(self, user_id):
        """Get remaining requests without incrementing."""
        key = self._get_cache_key(user_id)
        current = cache.get(key, 0)
        return max(0, self.config['count'] - current)