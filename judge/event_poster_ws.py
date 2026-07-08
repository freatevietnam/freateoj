import json
import logging
import threading
import urllib.request

from django.conf import settings

__all__ = ['EventPostingError', 'EventPoster', 'post', 'last']
_local = threading.local()
logger = logging.getLogger('judge.event')


class EventPostingError(RuntimeError):
    pass


class EventPoster(object):
    def __init__(self):
        pass

    def _post_url(self):
        return settings.EVENT_DAEMON_POST.rstrip('/')

    def post(self, channel, message, tries=0):
        try:
            url = self._post_url() + '/post'
            payload = json.dumps({'command': 'post', 'channel': channel, 'message': message}).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('status') == 'error':
                    raise EventPostingError(data.get('code', 'unknown'))
                return data.get('id', 0)
        except Exception as e:
            logger.error('Failed to post event to %s: %s', url, e)
            if tries > 3:
                raise
            return self.post(channel, message, tries + 1)

    def last(self, tries=0):
        try:
            url = self._post_url() + '/post'
            payload = json.dumps({'command': 'last-msg'}).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('status') == 'error':
                    raise EventPostingError(data.get('code', 'unknown'))
                return data.get('id', 0)
        except Exception as e:
            logger.error('Failed to get last msg from %s: %s', url, e)
            if tries > 3:
                raise
            return self.last(tries + 1)


def _get_poster():
    if 'poster' not in _local.__dict__:
        _local.poster = EventPoster()
    return _local.poster


def post(channel, message):
    try:
        return _get_poster().post(channel, message)
    except Exception:
        try:
            del _local.poster
        except AttributeError:
            pass
    return 0


def last():
    try:
        return _get_poster().last()
    except Exception:
        try:
            del _local.poster
        except AttributeError:
            pass
    return 0
