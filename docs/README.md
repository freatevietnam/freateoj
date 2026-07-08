# FreateOJ Documentation

## Cache Configuration

### Cache Versioning

Cache versioning allows you to invalidate all cached data when deploying new code. This ensures users get fresh data after updates.

**How it works:**
- `KEY_PREFIX`: A prefix added to all cache keys to avoid collisions with other apps
- `VERSION`: An integer that gets appended to cache keys. Increase this to invalidate all cache.

**When to increment VERSION:**
- After deploying code changes that affect cached data
- After database migrations that change cached models
- When you need to force a full cache refresh

### Example Configurations

#### Redis (Recommended for Production)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'KEY_PREFIX': 'freateoj',
        'VERSION': 1,  # Increase to invalidate cache
    },
}
```

#### Memcached

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'freateoj',
        'VERSION': 1,
    },
}
```

#### Local Memory (Development Only)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'KEY_PREFIX': 'freateoj',
        'VERSION': 1,
    },
}
```

### Deploy Checklist

1. Update `VERSION` in CACHES config
2. Deploy code
3. (Optional) Run `python manage.py shell -c "from django.core.cache import cache; cache.clear()"` to manually clear cache

### Per-Site Cache Keys

The project uses the following cache key patterns:

| Key Pattern | Purpose |
|-------------|---------|
| `freateoj:1:*` | Versioned cache entries (default) |
| `problem:*` | Problem data cache |
| `contest:*` | Contest data cache |
| `user:*` | User profile cache |

When you increment `VERSION`, all keys prefixed with `freateoj:1:` become inaccessible, and new keys will use `freateoj:2:`.
