from django.core.cache import cache


class CacheFactory:
    def __init__(self, key):
        self._key = key

    def get_cache_key(self):
        return self._key

    def get_cache(self):
        return cache.get(self.get_cache_key())

    def set_cache(self, data, timeout_s=3600):
        cache.set(self.get_cache_key(), data, timeout_s)

    def delete_cache(self):
        cache_key = self.get_cache_key()
        cache.delete(cache_key)


def unread_notification_count_cache_factory(profile_id):
    return CacheFactory(f'unread_notification_count_{profile_id}')


def notification_list_cache_factory(profile_id):
    return CacheFactory(f'notification_list_{profile_id}')


def bulk_invalidate_notification_caches(profile_ids):
    for pid in profile_ids:
        factory = unread_notification_count_cache_factory(pid)
        factory.delete_cache()
