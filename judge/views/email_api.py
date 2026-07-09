import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from judge.tasks.email import send_email_task
from judge.utils.rate_limit import EmailRateLimiter

logger = logging.getLogger(__name__)


@require_POST
@login_required
def send_email(request):
    """
    POST /api/email/send/
    Body: {email_type: str, ...context_data}
    Response: {task_id: str, status: str}
    """
    email_type = request.POST.get('email_type')

    # Validate email type
    valid_types = ['registration', 'resend_verification', 'password_reset', 'ticket']
    if email_type not in valid_types:
        return JsonResponse({'error': 'Invalid email type'}, status=400)

    # Rate limit check (only check remaining, don't increment yet - task will increment)
    limiter = EmailRateLimiter(email_type)
    remaining = limiter.get_remaining(request.user.id)
    if remaining <= 0:
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'remaining': remaining,
        }, status=429)

    # Build context
    context = {
        'user': request.user,
    }

    # Add extra context based on email_type
    if email_type == 'registration':
        context['otp_code'] = request.POST.get('otp_code', '')
        context['expires_minutes'] = request.POST.get('expires_minutes', 60)
    elif email_type == 'resend_verification':
        context['otp_code'] = request.POST.get('otp_code', '')
        context['expires_minutes'] = request.POST.get('expires_minutes', 60)
    elif email_type == 'password_reset':
        context['uid'] = request.POST.get('uid', '')
        context['token'] = request.POST.get('token', '')
    elif email_type == 'ticket':
        context['ticket_id'] = request.POST.get('ticket_id', '')
        context['message'] = request.POST.get('message', '')

    # Queue task
    try:
        task = send_email_task.delay(email_type, request.user.id, context)
        return JsonResponse({
            'task_id': task.id,
            'status': 'queued',
            'remaining': remaining,
        })
    except (ConnectionRefusedError, OSError) as e:
        logger.warning(f'Celery not available: {e}')
        return JsonResponse({
            'error': 'Email service temporarily unavailable',
        }, status=503)


@require_GET
@login_required
def email_status(request, task_id):
    """
    GET /api/email/status/<task_id>/
    Response: {status: str, progress: int}
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id)

    if result.state == 'PROGRESS':
        return JsonResponse({
            'status': 'processing',
            'progress': result.info.get('progress', 0),
        })
    elif result.state == 'SUCCESS':
        return JsonResponse({
            'status': 'success',
            'progress': 100,
            'result': result.result,
        })
    elif result.state == 'FAILURE':
        return JsonResponse({
            'status': 'error',
            'error': str(result.info),
        })
    else:
        return JsonResponse({
            'status': 'queued',
            'progress': 0,
        })
