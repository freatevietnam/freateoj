# Email Progress Bar & Socket.IO Notification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement non-blocking email sending with real-time progress tracking and Socket.IO notifications.

**Architecture:** Celery tasks for async email processing, Socket.IO for real-time notifications, Django cache for rate limiting, jQuery frontend with progress bar UI.

**Tech Stack:** Python/Django, Celery, Socket.IO (socket.io), jQuery, Django cache framework

## Global Constraints

- EMAIL_SEND_TIMEOUT = 60 seconds (configurable in settings.py)
- EMAIL_RATE_LIMITS = {registration: 3/300s, resend_verification: 3/300s, password_reset: 5/300s, ticket: 10/60s}
- No database migrations required
- Must work with existing Socket.IO daemon (websocket/daemon.js)
- Follow existing code style and patterns

---

## File Structure

### New Files
- `judge/utils/rate_limit.py` - Rate limiter utility class
- `judge/tasks/__init__.py` - Tasks package init
- `judge/tasks/email.py` - Celery email tasks
- `judge/views/email_api.py` - Email API endpoints
- `judge/utils/socket_events.py` - Socket.IO event emitter
- `resources/email-progress.js` - Frontend JavaScript
- `resources/email-progress.css` - Progress bar styles

### Modified Files
- `dmoj/settings.py` - Add EMAIL_SEND_TIMEOUT and EMAIL_RATE_LIMITS
- `dmoj/urls.py` - Add email API URLs
- `judge/__init__.py` - Import celery app (if needed)

---

### Task 1: Settings Configuration

**Files:**
- Modify: `dmoj/settings.py`

**Interfaces:**
- Produces: `EMAIL_SEND_TIMEOUT`, `EMAIL_RATE_LIMITS` settings

- [ ] **Step 1: Add email timeout setting**

Add after line 282 (`DMOJ_EMAIL_THROTTLING`):

```python
EMAIL_SEND_TIMEOUT = 60  # seconds
```

- [ ] **Step 2: Add rate limits configuration**

Add after `EMAIL_SEND_TIMEOUT`:

```python
# Rate limits per email API type
# count: max requests, window: time window in seconds
EMAIL_RATE_LIMITS = {
    'registration': {'count': 3, 'window': 300},        # 3 per 5 min
    'resend_verification': {'count': 3, 'window': 300},  # 3 per 5 min
    'password_reset': {'count': 5, 'window': 300},       # 5 per 5 min
    'ticket': {'count': 10, 'window': 60},               # 10 per min
}
```

- [ ] **Step 3: Verify settings load**

Run: `python -c "from django.conf import settings; print(settings.EMAIL_SEND_TIMEOUT, settings.EMAIL_RATE_LIMITS)"`

Expected: `60 {'registration': {'count': 3, 'window': 300}, ...}`

- [ ] **Step 4: Commit**

```bash
git add dmoj/settings.py
git commit -m "feat: add EMAIL_SEND_TIMEOUT and EMAIL_RATE_LIMITS settings"
```

---

### Task 2: Rate Limiter Utility

**Files:**
- Create: `judge/utils/rate_limit.py`

**Interfaces:**
- Produces: `EmailRateLimiter` class with `is_allowed(user_id)` and `get_remaining(user_id)` methods

- [ ] **Step 1: Create rate_limit.py**

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

- [ ] **Step 2: Verify import**

Run: `python -c "from judge.utils.rate_limit import EmailRateLimiter; print('OK')"`

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add judge/utils/rate_limit.py
git commit -m "feat: add EmailRateLimiter utility class"
```

---

### Task 3: Socket.IO Event Emitter

**Files:**
- Create: `judge/utils/socket_events.py`

**Interfaces:**
- Produces: `emit_email_event(task_id, event_type, data)` function

- [ ] **Step 1: Create socket_events.py**

```python
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
```

- [ ] **Step 2: Verify import**

Run: `python -c "from judge.utils.socket_events import emit_email_event; print('OK')"`

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add judge/utils/socket_events.py
git commit -m "feat: add Socket.IO event emitter for email notifications"
```

---

### Task 4: Celery Email Task

**Files:**
- Create: `judge/tasks/__init__.py`
- Create: `judge/tasks/email.py`

**Interfaces:**
- Consumes: `EmailRateLimiter`, `emit_email_event`
- Produces: `send_email_task` Celery task

- [ ] **Step 1: Create tasks package init**

Create `judge/tasks/__init__.py`:

```python
from .email import send_email_task

__all__ = ['send_email_task']
```

- [ ] **Step 2: Create email.py task**

Create `judge/tasks/email.py`:

```python
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from judge.utils.rate_limit import EmailRateLimiter
from judge.utils.socket_events import emit_email_event

logger = logging.getLogger(__name__)


def _get_email_config(email_type, context):
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
    """
    Send email asynchronously with progress tracking.
    
    Args:
        email_type: Type of email (registration, resend_verification, etc.)
        user_id: User ID for rate limiting
        context: Email context data (must include 'user' key)
    """
    try:
        # Update progress: Starting
        self.update_state(state='PROGRESS', meta={'progress': 10})
        emit_email_event(self.id, 'progress', {'progress': 10})
        
        # Rate limit check
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
        
        # Build email
        email_config = _get_email_config(email_type, context)
        
        self.update_state(state='PROGRESS', meta={'progress': 50})
        emit_email_event(self.id, 'progress', {'progress': 50})
        
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
        emit_email_event(self.id, 'success', {
            'email_type': email_type,
            'remaining': remaining,
        })
        
        return {
            'status': 'success',
            'email_type': email_type,
            'remaining': remaining,
        }
        
    except Exception as exc:
        logger.error(f'Failed to send {email_type} email: {exc}')
        emit_email_event(self.id, 'error', {'error': str(exc)})
        self.retry(exc=exc, countdown=60)
        return {
            'status': 'error',
            'error': str(exc),
        }
```

- [ ] **Step 3: Verify import**

Run: `python -c "from judge.tasks.email import send_email_task; print('OK')"`

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add judge/tasks/__init__.py judge/tasks/email.py
git commit -m "feat: add Celery email task with progress tracking"
```

---

### Task 5: Email API Endpoints

**Files:**
- Create: `judge/views/email_api.py`
- Modify: `dmoj/urls.py`

**Interfaces:**
- Consumes: `send_email_task`, `EmailRateLimiter`
- Produces: `send_email()`, `email_status()` views

- [ ] **Step 1: Create email_api.py**

Create `judge/views/email_api.py`:

```python
import logging
from django.conf import settings
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
    
    # Rate limit check
    limiter = EmailRateLimiter(email_type)
    allowed, remaining = limiter.is_allowed(request.user.id)
    if not allowed:
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
```

- [ ] **Step 2: Add URL patterns to dmoj/urls.py**

Add after line 442 (`path('misc_config/', ...)`):

```python
path('api/email/', include([
    path('send/', email_api.send_email, name='email_send'),
    path('status/<str:task_id>/', email_api.email_status, name='email_status'),
])),
```

Add import at top of urls.py (after line 14):

```python
from judge.views import email_api
```

- [ ] **Step 3: Verify URL configuration**

Run: `python manage.py show_urls | grep api/email`

Expected: `/api/email/send/` and `/api/email/status/<task_id>/`

- [ ] **Step 4: Commit**

```bash
git add judge/views/email_api.py dmoj/urls.py
git commit -m "feat: add email API endpoints with rate limiting"
```

---

### Task 6: Frontend JavaScript

**Files:**
- Create: `resources/email-progress.js`

**Interfaces:**
- Consumes: Socket.IO client, jQuery
- Produces: `window.EmailSender` public API

- [ ] **Step 1: Create email-progress.js**

Create `resources/email-progress.js`:

```javascript
(function() {
    'use strict';
    
    let socket = null;
    let currentTaskId = null;
    let pollInterval = null;
    let timeoutId = null;
    
    function initSocket() {
        if (typeof io !== 'undefined' && !socket) {
            socket = io();
            socket.on('connect', function() {
                console.log('Socket.IO connected for email notifications');
            });
        }
    }
    
    function showProgressBar() {
        if ($('#email-progress-modal').length) return;
        
        var html = '<div id="email-progress-modal" class="modal">' +
            '<div class="modal-content">' +
            '<h3>Sending Email...</h3>' +
            '<div class="progress-container">' +
            '<div class="progress-bar" id="email-progress-bar">' +
            '<span class="progress-text">0%</span>' +
            '</div>' +
            '</div>' +
            '<p id="email-status-text">Preparing to send...</p>' +
            '</div>' +
            '</div>';
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
    
    function showNotification(type, message) {
        var className = type === 'success' ? 'alert-success' : 'alert-danger';
        var html = '<div class="alert ' + className + '">' + message + '</div>';
        $('#email-progress-modal .modal-content').append(html);
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
            }
        });
        
        socket.on('email_error', function(data) {
            if (data.task_id === taskId) {
                hideProgressBar();
                showNotification('error', data.error || 'Failed to send email');
            }
        });
    }
    
    function pollStatus(taskId) {
        if (pollInterval) clearInterval(pollInterval);
        if (timeoutId) clearTimeout(timeoutId);
        
        var timeout = (window.EMAIL_SEND_TIMEOUT || 60) * 1000;
        
        pollInterval = setInterval(function() {
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
        
        timeoutId = setTimeout(function() {
            clearInterval(pollInterval);
            hideProgressBar();
            showNotification('error', 'Email sending timed out');
        }, timeout);
    }
    
    function cleanup() {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
        if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
        }
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
                data: $.extend({email_type: emailType}, data),
                success: function(resp) {
                    currentTaskId = resp.task_id;
                    updateProgress(10, 'Email queued');
                    subscribeToEmailEvents(resp.task_id);
                    pollStatus(resp.task_id);
                    if (callback) callback(null, resp);
                },
                error: function(xhr) {
                    hideProgressBar();
                    var error = (xhr.responseJSON && xhr.responseJSON.error) || 'Failed to send email';
                    showNotification('error', error);
                    if (callback) callback(error);
                }
            });
        },
        
        cancel: function() {
            cleanup();
            hideProgressBar();
            if (socket && currentTaskId) {
                socket.emit('unsubscribe', {channels: ['email:' + currentTaskId]});
            }
        }
    };
})();
```

- [ ] **Step 2: Add EMAIL_SEND_TIMEOUT to window**

In the same file, at the end of the IIFE, add:

```javascript
    // Set timeout from Django settings
    window.EMAIL_SEND_TIMEOUT = 60;  // Default, will be overridden by template
```

- [ ] **Step 3: Commit**

```bash
git add resources/email-progress.js
git commit -m "feat: add email progress bar JavaScript with Socket.IO"
```

---

### Task 7: Frontend CSS

**Files:**
- Create: `resources/email-progress.css`

**Interfaces:**
- Consumes: None
- Produces: CSS styles for progress modal

- [ ] **Step 1: Create email-progress.css**

Create `resources/email-progress.css`:

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

#email-progress-modal .alert {
    margin-top: 1rem;
    padding: 0.5rem;
    border-radius: 4px;
}

#email-progress-modal .alert-success {
    background-color: #d4edda;
    color: #155724;
}

#email-progress-modal .alert-danger {
    background-color: #f8d7da;
    color: #721c24;
}
```

- [ ] **Step 2: Commit**

```bash
git add resources/email-progress.css
git commit -m "feat: add email progress bar CSS styles"
```

---

### Task 8: Integration Testing

**Files:**
- Test: Manual testing checklist

**Interfaces:**
- Consumes: All previous tasks

- [ ] **Step 1: Start services**

```bash
# Terminal 1: Start Celery worker
celery -A dmoj worker -l info

# Terminal 2: Start Socket.IO daemon
node websocket/daemon.js

# Terminal 3: Start Django
python manage.py runserver
```

- [ ] **Step 2: Test rate limiting**

```bash
# Send 4 requests quickly (should fail on 4th)
for i in {1..4}; do
  curl -X POST http://localhost:8000/api/email/send/ \
    -H "Cookie: sessionid=..." \
    -d "email_type=registration"
  echo ""
done
```

Expected: First 3 return 200, 4th returns 429

- [ ] **Step 3: Test progress bar**

1. Login to Django admin
2. Navigate to a page that uses EmailSender
3. Trigger email send
4. Verify progress bar appears and updates
5. Verify Socket.IO notifications work

- [ ] **Step 4: Test timeout**

1. Mock a slow email send (>60s)
2. Verify timeout message appears

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete email progress and notification system"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Settings configuration | `dmoj/settings.py` |
| 2 | Rate limiter utility | `judge/utils/rate_limit.py` |
| 3 | Socket.IO event emitter | `judge/utils/socket_events.py` |
| 4 | Celery email task | `judge/tasks/email.py` |
| 5 | Email API endpoints | `judge/views/email_api.py`, `dmoj/urls.py` |
| 6 | Frontend JavaScript | `resources/email-progress.js` |
| 7 | Frontend CSS | `resources/email-progress.css` |
| 8 | Integration testing | Manual testing |
