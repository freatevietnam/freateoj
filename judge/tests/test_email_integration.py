from unittest.mock import patch, MagicMock, call
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse

from judge.views.email_api import send_email, email_status, TASK_OWNER_PREFIX
from judge.tasks.email import send_email_task
from judge.utils.rate_limit import EmailRateLimiter
from judge.utils.socket_events import emit_email_event


@override_settings(
    EMAIL_RATE_LIMITS={
        'registration': {'count': 3, 'window': 300},
        'resend_verification': {'count': 3, 'window': 300},
        'password_reset': {'count': 5, 'window': 300},
        'ticket': {'count': 10, 'window': 60},
    },
    EMAIL_SEND_TIMEOUT=60,
    EVENT_DAEMON_USE=True,
    EVENT_DAEMON_POST='http://localhost:9996/',
)
class EmailIntegrationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cache.clear()

    def test_rate_limiter_allows_requests_within_limit(self):
        limiter = EmailRateLimiter('registration')
        
        # Should allow first 3 requests
        for i in range(3):
            allowed, remaining = limiter.is_allowed(self.user.id)
            self.assertTrue(allowed)
            self.assertEqual(remaining, 2 - i)
        
        # 4th request should be denied
        allowed, remaining = limiter.is_allowed(self.user.id)
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)

    def test_rate_limiter_different_users_independent(self):
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        limiter = EmailRateLimiter('registration')
        
        # User 1 uses all requests
        for i in range(3):
            allowed, _ = limiter.is_allowed(self.user.id)
            self.assertTrue(allowed)
        
        # User 2 should still have requests
        allowed, remaining = limiter.is_allowed(user2.id)
        self.assertTrue(allowed)
        self.assertEqual(remaining, 2)

    def test_rate_limiter_different_email_types_independent(self):
        limiter_reg = EmailRateLimiter('registration')
        limiter_ticket = EmailRateLimiter('ticket')
        
        # Use all registration requests
        for i in range(3):
            allowed, _ = limiter_reg.is_allowed(self.user.id)
            self.assertTrue(allowed)
        
        # Ticket requests should still work
        allowed, remaining = limiter_ticket.is_allowed(self.user.id)
        self.assertTrue(allowed)
        self.assertEqual(remaining, 9)

    def test_rate_limiter_get_remaining_does_not_increment(self):
        limiter = EmailRateLimiter('registration')
        
        # Check remaining without incrementing
        remaining = limiter.get_remaining(self.user.id)
        self.assertEqual(remaining, 3)
        
        # Check again - should still be 3
        remaining = limiter.get_remaining(self.user.id)
        self.assertEqual(remaining, 3)
        
        # Now increment
        allowed, _ = limiter.is_allowed(self.user.id)
        self.assertTrue(allowed)
        
        # Check remaining - should be 2
        remaining = limiter.get_remaining(self.user.id)
        self.assertEqual(remaining, 2)

    @patch('judge.views.email_api.send_email_task')
    def test_send_email_api_success(self, mock_task):
        mock_task.delay.return_value.id = 'test-task-id-123'
        
        request = self.factory.post(
            '/api/email/send/',
            {
                'email_type': 'registration',
                'otp_code': '123456',
                'expires_minutes': 30,
            }
        )
        request.user = self.user
        
        response = send_email(request)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['task_id'], 'test-task-id-123')
        self.assertEqual(data['status'], 'queued')
        self.assertIn('remaining', data)
        
        # Verify task ownership is stored in cache
        cache_key = f'{TASK_OWNER_PREFIX}test-task-id-123'
        owner_id = cache.get(cache_key)
        self.assertEqual(owner_id, self.user.id)

    def test_send_email_api_invalid_type(self):
        request = self.factory.post(
            '/api/email/send/',
            {'email_type': 'invalid_type'}
        )
        request.user = self.user
        
        response = send_email(request)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    @patch('judge.views.email_api.send_email_task')
    def test_send_email_api_rate_limited(self, mock_task):
        # Use up all rate limits
        limiter = EmailRateLimiter('registration')
        for i in range(3):
            limiter.is_allowed(self.user.id)
        
        request = self.factory.post(
            '/api/email/send/',
            {'email_type': 'registration'}
        )
        request.user = self.user
        
        response = send_email(request)
        
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['remaining'], 0)
        
        # Task should not have been called
        mock_task.delay.assert_not_called()

    def test_send_email_api_requires_login(self):
        request = self.factory.post(
            '/api/email/send/',
            {'email_type': 'registration'}
        )
        # Don't set request.user - simulates unauthenticated request
        
        response = send_email(request)
        
        # Should redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])

    @patch('judge.views.email_api.AsyncResult')
    def test_email_status_api_success(self, mock_result):
        task_id = 'test-task-id-456'
        cache_key = f'{TASK_OWNER_PREFIX}{task_id}'
        cache.set(cache_key, self.user.id, 3600)
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        mock_result.return_value.state = 'QUEUED'
        response = email_status(request, task_id)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'queued')
        self.assertEqual(data['progress'], 0)

    @patch('judge.views.email_api.AsyncResult')
    def test_email_status_api_processing(self, mock_result):
        task_id = 'test-task-id-789'
        cache_key = f'{TASK_OWNER_PREFIX}{task_id}'
        cache.set(cache_key, self.user.id, 3600)
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        mock_result.return_value.state = 'PROGRESS'
        mock_result.return_value.info = {'progress': 50}
        response = email_status(request, task_id)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'processing')
        self.assertEqual(data['progress'], 50)

    @patch('judge.views.email_api.AsyncResult')
    def test_email_status_api_success_completed(self, mock_result):
        task_id = 'test-task-id-101'
        cache_key = f'{TASK_OWNER_PREFIX}{task_id}'
        cache.set(cache_key, self.user.id, 3600)
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        mock_result.return_value.state = 'SUCCESS'
        mock_result.return_value.result = {'status': 'success', 'email_type': 'registration'}
        response = email_status(request, task_id)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['progress'], 100)
        self.assertIn('result', data)

    @patch('judge.views.email_api.AsyncResult')
    def test_email_status_api_failure(self, mock_result):
        task_id = 'test-task-id-202'
        cache_key = f'{TASK_OWNER_PREFIX}{task_id}'
        cache.set(cache_key, self.user.id, 3600)
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        mock_result.return_value.state = 'FAILURE'
        mock_result.return_value.info = Exception('Email send failed')
        response = email_status(request, task_id)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('error', data)

    def test_email_status_api_non_owner_access(self):
        task_id = 'test-task-id-303'
        cache_key = f'{TASK_OWNER_PREFIX}{task_id}'
        cache.set(cache_key, 9999, 3600)  # Different user ID
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        response = email_status(request, task_id)
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)

    def test_email_status_api_no_task(self):
        task_id = 'non-existent-task-id'
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        response = email_status(request, task_id)
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)

    def test_email_status_api_requires_login(self):
        task_id = 'test-task-id-404'
        request = self.factory.get(f'/api/email/status/{task_id}/')
        # Don't set request.user
        
        response = email_status(request, task_id)
        
        # Should redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])


@override_settings(
    EMAIL_RATE_LIMITS={
        'registration': {'count': 3, 'window': 300},
    },
    EMAIL_SEND_TIMEOUT=60,
    EVENT_DAEMON_USE=True,
    EVENT_DAEMON_POST='http://localhost:9996/',
)
class CeleryEmailTaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cache.clear()

    @patch('judge.tasks.email.send_mail')
    @patch('judge.tasks.email.emit_email_event')
    def test_send_email_task_success(self, mock_emit, mock_send_mail):
        context = {
            'otp_code': '123456',
            'expires_minutes': 30,
        }
        
        task = MagicMock()
        task.id = 'test-task-id'
        
        result = send_email_task(task, 'registration', self.user.id, context)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['email_type'], 'registration')
        
        # Verify user was added to context
        self.assertIn('user', context)
        self.assertEqual(context['user'].id, self.user.id)
        
        # Verify send_mail was called
        mock_send_mail.assert_called_once()
        
        # Verify progress events were emitted
        self.assertTrue(mock_emit.called)
        calls = mock_emit.call_args_list
        self.assertEqual(calls[0], call('test-task-id', 'progress', {'progress': 10}))
        self.assertEqual(calls[1], call('test-task-id', 'progress', {'progress': 30}))
        self.assertEqual(calls[2], call('test-task-id', 'progress', {'progress': 50}))
        self.assertEqual(calls[3], call('test-task-id', 'success', {'email_type': 'registration', 'remaining': 2}))

    @patch('judge.tasks.email.emit_email_event')
    def test_send_email_task_user_not_found(self, mock_emit):
        context = {
            'otp_code': '123456',
            'expires_minutes': 30,
        }
        
        task = MagicMock()
        task.id = 'test-task-id'
        
        result = send_email_task(task, 'registration', 99999, context)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('not found', result['error'])
        
        # Verify error event was emitted
        mock_emit.assert_called_with('test-task-id', 'error', {'error': 'User with id 99999 not found.'})

    @patch('judge.tasks.email.send_mail')
    @patch('judge.tasks.email.emit_email_event')
    def test_send_email_task_rate_limited(self, mock_emit, mock_send_mail):
        # Use up all rate limits
        limiter = EmailRateLimiter('registration')
        for i in range(3):
            limiter.is_allowed(self.user.id)
        
        context = {
            'otp_code': '123456',
            'expires_minutes': 30,
        }
        
        task = MagicMock()
        task.id = 'test-task-id'
        
        result = send_email_task(task, 'registration', self.user.id, context)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Rate limit exceeded', result['error'])
        
        # Verify send_mail was not called
        mock_send_mail.assert_not_called()
        
        # Verify error event was emitted
        mock_emit.assert_called_with('test-task-id', 'error', {'error': 'Rate limit exceeded. Please try again later.'})

    @patch('judge.tasks.email.send_mail')
    @patch('judge.tasks.email.emit_email_event')
    def test_send_email_task_different_email_types(self, mock_emit, mock_send_mail):
        email_types = ['registration', 'resend_verification', 'password_reset', 'ticket']
        
        for email_type in email_types:
            cache.clear()
            
            context = {}
            
            if email_type in ['registration', 'resend_verification']:
                context['otp_code'] = '123456'
                context['expires_minutes'] = 30
            elif email_type == 'password_reset':
                context['uid'] = 'testuid'
                context['token'] = 'testtoken'
            elif email_type == 'ticket':
                context['ticket_id'] = '123'
                context['message'] = 'Test message'
            
            task = MagicMock()
            task.id = f'test-task-{email_type}'
            
            result = send_email_task(task, email_type, self.user.id, context)
            
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['email_type'], email_type)
            self.assertIn('user', context)


@override_settings(
    EVENT_DAEMON_USE=True,
    EVENT_DAEMON_POST='http://localhost:9996/',
)
class SocketIOEventTestCase(TestCase):
    @patch('judge.utils.socket_events.requests')
    def test_emit_email_event_success(self, mock_requests):
        mock_requests.post.return_value = MagicMock(status_code=200)
        
        emit_email_event('task-123', 'progress', {'progress': 50})
        
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        self.assertEqual(call_args[0][0], 'http://localhost:9996/')
        
        json_data = call_args[1]['json']
        self.assertEqual(json_data['command'], 'post')
        self.assertEqual(json_data['channel'], 'email:task-123')
        self.assertEqual(json_data['message']['type'], 'email_progress')
        self.assertEqual(json_data['message']['task_id'], 'task-123')
        self.assertEqual(json_data['message']['progress'], 50)

    @patch('judge.utils.socket_events.requests')
    def test_emit_email_event_error(self, mock_requests):
        mock_requests.post.return_value = MagicMock(status_code=200)
        
        emit_email_event('task-456', 'error', {'error': 'Something went wrong'})
        
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        json_data = call_args[1]['json']
        self.assertEqual(json_data['message']['type'], 'email_error')
        self.assertEqual(json_data['message']['error'], 'Something went wrong')

    @patch('judge.utils.socket_events.requests')
    def test_emit_email_event_success_event(self, mock_requests):
        mock_requests.post.return_value = MagicMock(status_code=200)
        
        emit_email_event('task-789', 'success', {'email_type': 'registration', 'remaining': 2})
        
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        json_data = call_args[1]['json']
        self.assertEqual(json_data['message']['type'], 'email_success')
        self.assertEqual(json_data['message']['email_type'], 'registration')
        self.assertEqual(json_data['message']['remaining'], 2)

    @patch('judge.utils.socket_events.requests')
    def test_emit_email_event_disabled(self, mock_requests):
        with override_settings(EVENT_DAEMON_USE=False):
            emit_email_event('task-999', 'progress', {'progress': 10})
            
            # Should not make any HTTP request
            mock_requests.post.assert_not_called()

    @patch('judge.utils.socket_events.requests')
    def test_emit_email_event_handles_exception(self, mock_requests):
        mock_requests.post.side_effect = Exception('Connection refused')
        
        # Should not raise exception
        emit_email_event('task-101', 'progress', {'progress': 10})
        
        # Should have attempted to make the request
        mock_requests.post.assert_called_once()


@override_settings(
    EMAIL_RATE_LIMITS={
        'registration': {'count': 3, 'window': 300},
    },
    EMAIL_SEND_TIMEOUT=60,
    EVENT_DAEMON_USE=True,
    EVENT_DAEMON_POST='http://localhost:9996/',
)
class EndToEndIntegrationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cache.clear()

    @patch('judge.tasks.email.send_mail')
    @patch('judge.utils.socket_events.requests')
    def test_full_email_flow(self, mock_requests, mock_send_mail):
        mock_requests.post.return_value = MagicMock(status_code=200)
        
        # Step 1: Send email via API
        request = self.factory.post(
            '/api/email/send/',
            {
                'email_type': 'registration',
                'otp_code': '123456',
                'expires_minutes': 30,
            }
        )
        request.user = self.user
        
        response = send_email(request)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        task_id = data['task_id']
        
        # Step 2: Execute the Celery task directly (simulating Celery worker)
        context = {
            'otp_code': '123456',
            'expires_minutes': 30,
        }
        
        task = MagicMock()
        task.id = task_id
        
        result = send_email_task(task, 'registration', self.user.id, context)
        
        # Step 3: Verify the result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['email_type'], 'registration')
        
        # Step 4: Verify Socket.IO events were emitted
        self.assertTrue(mock_requests.post.called)
        
        # Verify email was sent
        mock_send_mail.assert_called_once()
        
        # Step 5: Check task status via API
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        # Mock the Celery result for the status check
        with patch('judge.views.email_api.AsyncResult') as mock_result:
            mock_result.return_value.state = 'SUCCESS'
            mock_result.return_value.result = result
            
            response = email_status(request, task_id)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['progress'], 100)

    @patch('judge.utils.socket_events.requests')
    def test_rate_limiting_prevents_email_sending(self, mock_requests):
        mock_requests.post.return_value = MagicMock(status_code=200)
        
        # Use up all rate limits
        limiter = EmailRateLimiter('registration')
        for i in range(3):
            limiter.is_allowed(self.user.id)
        
        # Try to send email
        request = self.factory.post(
            '/api/email/send/',
            {'email_type': 'registration'}
        )
        request.user = self.user
        
        response = send_email(request)
        self.assertEqual(response.status_code, 429)
        
        # Verify no Socket.IO events were emitted
        mock_requests.post.assert_not_called()
