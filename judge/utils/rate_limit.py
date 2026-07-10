from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


class RateLimiter:
    """Generic rate limiter using Django cache."""

    def __init__(self, api_type, config_dict=None):
        if config_dict is None:
            config_dict = getattr(settings, 'RATE_LIMITS', {})
        
        if api_type not in config_dict:
            raise ValueError(f'Unknown API type: {api_type}')
        self.api_type = api_type
        self.config = config_dict[api_type]

    def _get_cache_key(self, identifier):
        return f'rate_limit:{self.api_type}:{identifier}'

    def is_allowed(self, identifier):
        """Check if request is allowed. Returns (allowed: bool, remaining: int)."""
        key = self._get_cache_key(identifier)
        current = cache.get(key, 0)
        
        if current >= self.config['count']:
            return False, 0
        
        # Increment counter
        if current == 0:
            cache.set(key, 1, self.config['window'])
        else:
            cache.incr(key)
        
        return True, self.config['count'] - current - 1

    def get_remaining(self, identifier):
        """Get remaining requests without incrementing."""
        key = self._get_cache_key(identifier)
        current = cache.get(key, 0)
        return max(0, self.config['count'] - current)


class EmailRateLimiter(RateLimiter):
    """Rate limiter for email APIs."""

    def __init__(self, api_type):
        super().__init__(api_type, getattr(settings, 'EMAIL_RATE_LIMITS', {}))

    def _get_cache_key(self, user_id):
        return f'email_rate:{self.api_type}:{user_id}'


def rate_limit(api_type, identifier_func=None):
    """
    Decorator for rate limiting views.
    
    Args:
        api_type: Key in RATE_LIMITS settings
        identifier_func: Function that takes request and returns identifier.
                        Defaults to request.user.id for logged-in users, 
                        request.META['REMOTE_ADDR'] for anonymous.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            limiter = RateLimiter(api_type)
            
            # Get identifier
            if identifier_func:
                identifier = identifier_func(request)
            elif request.user.is_authenticated:
                identifier = request.user.id
            else:
                identifier = request.META.get('REMOTE_ADDR', 'unknown')
            
            allowed, remaining = limiter.is_allowed(identifier)
            
            if not allowed:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': limiter.config['window'],
                }, status=429)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
