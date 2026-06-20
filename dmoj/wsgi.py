import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402, django must be imported here
application = get_wsgi_application()
