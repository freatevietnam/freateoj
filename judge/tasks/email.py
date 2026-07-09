import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from judge.utils.rate_limit import EmailRateLimiter
from judge.utils.socket_events import emit_email_event

logger = logging.getLogger(__name__)


def _get_email_config(email_type, context):
    site_name = getattr(settings, 'SITE_NAME', 'FreateOJ')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@freate.io.vn')

    configs = {
        'registration': {
            'subject': f'Verify your {site_name} email address',
            'template': 'registration/verification_email',
        },
        'resend_verification': {
            'subject': f'Verify your {site_name} email address',
            'template': 'registration/verification_email',
        },
        'password_reset': {
            'subject': f'Password reset for {site_name}',
            'template': 'registration/password_reset_email',
        },
        'ticket': {
            'subject': f'[{site_name}] Ticket Update',
            'template': 'ticket/email_update',
        },
    }

    config = configs.get(email_type)
    if not config:
        raise ValueError(f'Unknown email type: {email_type}')

    text_message = render_to_string(f'{config["template"]}.txt', context)
    html_message = render_to_string(f'{config["template"]}.html', context)

    return {
        'subject': config['subject'],
        'text_message': text_message,
        'html_message': html_message,
        'from_email': from_email,
        'recipient': context['user'].email,
    }


@shared_task(bind=True, max_retries=3)
def send_email_task(self, email_type, user_id, context):
    try:
        self.update_state(state='PROGRESS', meta={'progress': 10})
        emit_email_event(self.id, 'progress', {'progress': 10})

        limiter = EmailRateLimiter(email_type)
        allowed, remaining = limiter.is_allowed(user_id)
        if not allowed:
            error_msg = 'Rate limit exceeded. Please try again later.'
            emit_email_event(self.id, 'error', {'error': error_msg})
            return {
                'status': 'error',
                'error': error_msg,
            }

        self.update_state(state='PROGRESS', meta={'progress': 30})
        emit_email_event(self.id, 'progress', {'progress': 30})

        email_config = _get_email_config(email_type, context)

        self.update_state(state='PROGRESS', meta={'progress': 50})
        emit_email_event(self.id, 'progress', {'progress': 50})

        send_mail(
            subject=email_config['subject'],
            message=email_config['text_message'],
            from_email=email_config['from_email'],
            recipient_list=[email_config['recipient']],
            html_message=email_config['html_message'],
            fail_silently=False,
        )

        self.update_state(state='PROGRESS', meta={'progress': 100})
        emit_email_event(self.id, 'success', {'email_type': email_type, 'remaining': remaining})

        return {
            'status': 'success',
            'email_type': email_type,
            'remaining': remaining,
        }

    except Exception as exc:
        logger.error(f'Failed to send {email_type} email: {exc}')
        emit_email_event(self.id, 'error', {'error': str(exc)})
        self.retry(exc=exc, countdown=60)
