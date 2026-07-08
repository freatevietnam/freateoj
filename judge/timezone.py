import pytz
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import make_aware, make_naive


class TimezoneMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def get_timezone(self, request):
        tzname = settings.DEFAULT_USER_TIME_ZONE
        if request.profile:
            tzname = request.profile.timezone
        return pytz.timezone(tzname)

    def __call__(self, request):
        with timezone.override(self.get_timezone(request)):
            return self.get_response(request)


def from_database_time(datetime):
    if datetime is None:
        return datetime
    # PostgreSQL with USE_TZ=True returns naive UTC datetimes from raw SQL.
    # Make them timezone-aware with UTC.
    if timezone.is_naive(datetime):
        return make_aware(datetime, pytz.utc)
    return datetime


def to_database_time(datetime):
    if datetime is None:
        return datetime
    # Convert aware datetime to naive UTC for PostgreSQL raw SQL queries.
    if timezone.is_aware(datetime):
        return make_naive(datetime, pytz.utc)
    return datetime
