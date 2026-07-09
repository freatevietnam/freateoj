# Email Progress Bar & Socket.IO Notification System

## Overview

Implement a non-blocking email sending system with real-time progress tracking and notifications using Celery tasks and Socket.IO. When users click "Send Email", they see a progress bar instead of waiting, and receive real-time notifications for success/failure.

## Goals

1. Non-blocking email sending with visual progress feedback
2. Real-time success/failure notifications via Socket.IO
3. Configurable email timeout per API
4. Rate limiting for all email endpoints to prevent spam/abuse

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│  Django API  │────▶│   Celery    │
│  (jQuery)   │◀────│  (Views)     │◀────│   Worker    │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                       │
       │            ┌──────────────┐           │
       └───────────▶│  Socket.IO   │◀──────────┘
                    │   Server     │
                    └──────────────┘
```

## Components

### 1. Settings Configuration

Add to `dmoj/settings.py`:

```python
# Email sending timeout (seconds)
EMAIL_SEND_TIMEOUT = 60

# Rate limits per API type
# count: max requests, window: time window in seconds
EMAIL_RATE_LIMITS = {
    'registration': {'count': 3, 'window': 300},        # 3 per 5 min
    'resend_verification': {'count': 3, 'window': 300},  # 3 per 5 min
    'password_reset': {'count': 5, 'window': 300},       # 5 per 5 min
    'ticket': {'count': 10, 'window': 60},               # 10 per min
}
```

### 2. Rate Limiter Utility

New file: `judge/utils/rate_limit.py`

```python
from django.conf import settings
from django.core.cache import cache


class EmailRateLimiter:
    """Rate limiter for email APIs using Django cache."""

    def __init__(self, api_type):
        if api_type not in settings.EMAIL_RATE_LIMITS:
            raise ValueError(f'Unknown API type: {api_type}')
        self.api_type = api_type
        self.config = settings.EMAIL_RATE_LIMITS[api_type]

    def _get_cache_key(self, user_id):
        return f'email_rate:{self.api_type}:{user_id}'

    def is_allowed(self, user_id):
        """Check if request is allowed. Returns (allowed: bool, remaining: int)."""
        key = self._get_cache_key(user_id)
        current = cache.get(key, 0)
        
        if current >= self.config['count']:
            return False, 0
        
        # Increment counter
        if current == 0:
            cache.set(key, 1, self.config['window'])
        else:
            cache.incr(key)
        
        return True, self.config['count'] - current - 1

    def get_remaining(self, user_id):
        """Get remaining requests without incrementing."""
        key = self._get_cache_key(user_id)
        current = cache.get(key, 0)
        return max(0, self.config['count'] - current)
```

### 3. Celery Task

New file: `judge/tasks/email.py`

```python
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from judge.utils.rate_limit import EmailRateLimiter

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_task(self, email_type, user_id, context):
    """
    Send email asynchronously with progress tracking.
    
    Args:
        email_type: Type of email (registration, resend_verification, etc.)
        user_id: User ID for rate limiting
        context: Email context data
    """
    try:
        # Update progress: Starting
        self.update_state(state='PROGRESS', meta={'progress': 10})
        
        # Rate limit check
        limiter = EmailRateLimiter(email_type)
        allowed, remaining = limiter.is_allowed(user_id)
        if not allowed:
            return {
                'status': 'error',
                'error': 'Rate limit exceeded. Please try again later.',
            }
        
        self.update_state(state='PROGRESS', meta={'progress': 30})
        
        # Build email
        email_config = self._get_email_config(email_type, context)
        
        self.update_state(state='PROGRESS', meta={'progress': 50})
        
        # Send email
        send_mail(
            subject=email_config['subject'],
            message=email_config['text_message'],
            from_email=email_config['from_email'],
            recipient_list=[email_config['recipient']],
            html_message=email_config['html_message'],
            fail_silently=False,
        )
        
        self.update_state(state='PROGRESS', meta={'progress': 100})
        
        return {
            'status': 'success',
            'email_type': email_type,
            'remaining': remaining,
        }
        
    except Exception as exc:
        logger.error(f'Failed to send {email_type} email: {exc}')
        self.retry(exc=exc, countdown=60)
        return {
            'status': 'error',
            'error': str(exc),
        }

    def _get_email_config(self, email_type, context):
        """Build email configuration based on type."""
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
```

### 4. API Endpoints

Add to `judge/views/email_api.py`:

```python
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from judge.tasks.email import send_email_task
from judge.utils.rate_limit import EmailRateLimiter


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
    
    # Rate limit check
    limiter = EmailRateLimiter(email_type)
    allowed, remaining = limiter.is_allowed(request.user.id)
    if not allowed:
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'remaining': remaining,
        }, status=429)
    
    # Queue task
    context = {
        'user': request.user,
        # Add other context based on email_type
    }
    
    task = send_email_task.delay(email_type, request.user.id, context)
    
    return JsonResponse({
        'task_id': task.id,
        'status': 'queued',
        'remaining': remaining,
    })


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
```

### 5. URL Configuration

Add to `dmoj/urls.py`:

```python
path('api/email/', include([
    path('send/', email_api.send_email, name='email_send'),
    path('status/<str:task_id>/', email_api.email_status, name='email_status'),
])),
```

### 6. Socket.IO Integration

Add to `judge/utils/socket_events.py`:

```python
import requests
from django.conf import settings


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
    except Exception:
        pass  # Silent fail for non-critical notifications
```

Update Celery task to emit events:

```python
# In send_email_task, add after each update_state:
from judge.utils.socket_events import emit_email_event

emit_email_event(self.id, 'progress', {'progress': 50})
```

### 7. Frontend JavaScript

New file: `resources/email-progress.js`

```javascript
(function() {
    'use strict';
    
    let socket = null;
    let currentTaskId = null;
    
    function initSocket() {
        if (typeof io !== 'undefined' && !socket) {
            socket = io();
            socket.on('connect', function() {
                console.log('Socket.IO connected for email notifications');
            });
        }
    }
    
    function showProgressBar() {
        const html = `
            <div id="email-progress-modal" class="modal">
                <div class="modal-content">
                    <h3>Sending Email...</h3>
                    <div class="progress-container">
                        <div class="progress-bar" id="email-progress-bar">
                            <span class="progress-text">0%</span>
                        </div>
                    </div>
                    <p id="email-status-text">Preparing to send...</p>
                </div>
            </div>
        `;
        $('body').append(html);
        $('#email-progress-modal').show();
    }
    
    function updateProgress(progress, text) {
        $('#email-progress-bar').css('width', progress + '%');
        $('#email-progress-bar .progress-text').text(progress + '%');
        if (text) {
            $('#email-status-text').text(text);
        }
    }
    
    function hideProgressBar() {
        $('#email-progress-modal').remove();
    }
    
    function subscribeToEmailEvents(taskId) {
        if (!socket) return;
        
        socket.emit('subscribe', {channels: ['email:' + taskId]});
        
        socket.on('email_progress', function(data) {
            if (data.task_id === taskId) {
                updateProgress(data.progress, 'Sending...');
            }
        });
        
        socket.on('email_success', function(data) {
            if (data.task_id === taskId) {
                updateProgress(100, 'Email sent successfully!');
                setTimeout(hideProgressBar, 2000);
                showNotification('success', 'Email sent successfully');
            }
        });
        
        socket.on('email_error', function(data) {
            if (data.task_id === taskId) {
                hideProgressBar();
                showNotification('error', data.error || 'Failed to send email');
            }
        });
    }
    
    function showNotification(type, message) {
        const className = type === 'success' ? 'alert-success' : 'alert-danger';
        const html = `<div class="alert ${className}">${message}</div>`;
        $('#email-progress-modal .modal-content').append(html);
    }
    
    // Public API
    window.EmailSender = {
        send: function(emailType, data, callback) {
            initSocket();
            showProgressBar();
            updateProgress(0, 'Queuing email...');
            
            $.ajax({
                url: '/api/email/send/',
                method: 'POST',
                data: {
                    email_type: emailType,
                    ...data,
                },
                success: function(resp) {
                    currentTaskId = resp.task_id;
                    updateProgress(10, 'Email queued');
                    subscribeToEmailEvents(resp.task_id);
                    
                    // Fallback polling
                    pollStatus(resp.task_id);
                    
                    if (callback) callback(null, resp);
                },
                error: function(xhr) {
                    hideProgressBar();
                    const error = xhr.responseJSON?.error || 'Failed to send email';
                    showNotification('error', error);
                    if (callback) callback(error);
                }
            });
        },
        
        cancel: function() {
            hideProgressBar();
            if (socket && currentTaskId) {
                socket.emit('unsubscribe', {channels: ['email:' + currentTaskId]});
            }
        }
    };
    
    function pollStatus(taskId) {
        const pollInterval = setInterval(function() {
            $.get('/api/email/status/' + taskId + '/', function(resp) {
                if (resp.status === 'success') {
                    clearInterval(pollInterval);
                    updateProgress(100, 'Email sent successfully!');
                    setTimeout(hideProgressBar, 2000);
                } else if (resp.status === 'error') {
                    clearInterval(pollInterval);
                    hideProgressBar();
                    showNotification('error', resp.error);
                } else if (resp.status === 'processing') {
                    updateProgress(resp.progress, 'Sending...');
                }
            });
        }, 1000);
        
        // Timeout after EMAIL_SEND_TIMEOUT
        setTimeout(function() {
            clearInterval(pollInterval);
            hideProgressBar();
            showNotification('error', 'Email sending timed out');
        }, window.EMAIL_SEND_TIMEOUT * 1000 || 60000);
    }
})();
```

### 8. CSS Styles

Add to `resources/email-progress.css`:

```css
#email-progress-modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9999;
}

#email-progress-modal .modal-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 2rem;
    border-radius: 8px;
    min-width: 400px;
    text-align: center;
}

.progress-container {
    width: 100%;
    background: #e0e0e0;
    border-radius: 10px;
    margin: 1rem 0;
    overflow: hidden;
}

.progress-bar {
    width: 0%;
    height: 30px;
    background: linear-gradient(90deg, #4caf50, #8bc34a);
    border-radius: 10px;
    transition: width 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.progress-text {
    color: white;
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

#email-status-text {
    color: #666;
    margin-top: 1rem;
}
```

## Files to Create/Modify

### New Files
- `judge/utils/rate_limit.py` - Rate limiter utility
- `judge/tasks/email.py` - Celery email tasks
- `judge/views/email_api.py` - API endpoints
- `judge/utils/socket_events.py` - Socket.IO event emitter
- `resources/email-progress.js` - Frontend JavaScript
- `resources/email-progress.css` - Progress bar styles

### Modified Files
- `dmoj/settings.py` - Add EMAIL_SEND_TIMEOUT and EMAIL_RATE_LIMITS
- `dmoj/urls.py` - Add email API URLs
- `judge/celery.py` - Ensure email task is registered (if needed)

## Rate Limit Configuration

| API Type | Requests | Window | Description |
|----------|----------|--------|-------------|
| registration | 3 | 300s | New account registration |
| resend_verification | 3 | 300s | Resend verification email |
| password_reset | 5 | 300s | Password reset request |
| ticket | 10 | 60s | Ticket system emails |

## Email Timeout

Default timeout: 60 seconds (configurable via `EMAIL_SEND_TIMEOUT` in settings.py)

## Testing

1. **Unit Tests**: Rate limiter, Celery tasks
2. **Integration Tests**: API endpoints, Socket.IO events
3. **E2E Tests**: Full email flow with progress bar

## Migration Notes

- No database migrations required
- Celery must be running for async email sending
- Socket.IO server must be running for real-time notifications
- Fallback to sync sending if Celery is unavailable (optional)

## Security Considerations

- Rate limiting prevents spam/abuse
- CSRF protection on all endpoints
- Task IDs are UUIDs, not sequential
- Email content is rendered server-side only
