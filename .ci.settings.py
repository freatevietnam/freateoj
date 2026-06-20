COMPRESS_OUTPUT_DIR = 'cache'
STATICFILES_FINDERS += ('compressor.finders.CompressorFinder',)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dmoj',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': 5432,
    },
}
