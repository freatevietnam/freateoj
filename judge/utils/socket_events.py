import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def emit_email_event(task_id, event_type, data):
    """Emit email event to Socket.IO server."""
    if not getattr(settings, 'EVENT_DAEMON_USE', False):
        return

    channel = f'email:{task_id}'
    message = {
        'type': f'email_{event_type}',
        'task_id': task_id,
        **data,
    }

    try:
        requests.post(
            settings.EVENT_DAEMON_POST,
            json={
                'command': 'post',
                'channel': channel,
                'message': message,
            },
            timeout=5,
        )
    except Exception as e:
        logger.warning(f'Failed to emit email event: {e}')
