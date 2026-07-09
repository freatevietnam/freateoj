from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse

from judge.views.email_api import send_email, email_status, TASK_OWNER_PREFIX


class EmailApiTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Clear cache before each test
        cache.clear()

    @patch('judge.views.email_api.send_email_task')
    def test_send_email_success(self, mock_task):
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
        
        # Verify task ownership is stored in cache
        cache_key = f'{TASK_OWNER_PREFIX}test-task-id-123'
        owner_id = cache.get(cache_key)
        self.assertEqual(owner_id, self.user.id)
        
        # Verify context does not contain user object
        call_args = mock_task.delay.call_args
        context = call_args[0][2]  # Third argument is context
        self.assertNotIn('user', context)

    @patch('judge.views.email_api.send_email_task')
    def test_send_email_invalid_type(self, mock_task):
        request = self.factory.post(
            '/api/email/send/',
            {'email_type': 'invalid_type'}
        )
        request.user = self.user
        
        response = send_email(request)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_email_status_owner_access(self):
        task_id = 'test-task-id-456'
        cache_key = f'{TASK_OWNER_PREFIX}{task_id}'
        cache.set(cache_key, self.user.id, 3600)
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        with patch('judge.views.email_api.AsyncResult') as mock_result:
            mock_result.return_value.state = 'QUEUED'
            response = email_status(request, task_id)
            
            self.assertEqual(response.status_code, 200)

    def test_email_status_non_owner_access(self):
        task_id = 'test-task-id-789'
        cache_key = f'{TASK_OWNER_PREFIX}{task_id}'
        cache.set(cache_key, 9999, 3600)  # Different user ID
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        response = email_status(request, task_id)
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)

    def test_email_status_no_task(self):
        task_id = 'non-existent-task-id'
        
        request = self.factory.get(f'/api/email/status/{task_id}/')
        request.user = self.user
        
        response = email_status(request, task_id)
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)
