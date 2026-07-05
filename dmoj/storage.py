import posixpath

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ManifestStaticFilesStorageSafe(ManifestStaticFilesStorage):
    """
    A custom storage class that gracefully handles missing source map files.

    This fixes the issue where JavaScript files reference .map files that don't exist,
    causing collectstatic to fail with ManifestStaticFilesStorage.
    """

    def _stored_name(self, name, hashed_files):
        name = posixpath.normpath(name)
        cleaned_name = self.clean_name(name)
        hash_key = self.hash_key(cleaned_name)
        cache_name = hashed_files.get(hash_key)
        if cache_name is None:
            try:
                cache_name = self.clean_name(self.hashed_name(name))
            except ValueError:
                if ".map" in name:
                    cache_name = cleaned_name
                else:
                    raise
        return cache_name
