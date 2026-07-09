from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User

from judge.tasks.email import send_email_task, _get_email_config


class EmailTaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('judge.tasks.email.send_mail')
    @patch('judge.tasks.email.emit_email_event')
    def test_send_email_task_success(self, mock_emit, mock_send_mail):
        context = {
            'otp_code': '123456',
            'expires_minutes': 30,
        }
        
        # Mock the task object
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

    @patch('judge.tasks.email.emit_email_event')
    def test_send_email_task_user_not_found(self, mock_emit):
        context = {
            'otp_code': '123456',
            'expires_minutes': 30,
        }
        
        # Mock the task object
        task = MagicMock()
        task.id = 'test-task-id'
        
        # Use non-existent user ID
        result = send_email_task(task, 'registration', 99999, context)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('not found', result['error'])

    @patch('judge.tasks.email.send_mail')
    @patch('judge.tasks.email.emit_email_event')
    def test_send_email_task_different_email_types(self, mock_emit, mock_send_mail):
        email_types = ['registration', 'resend_verification', 'password_reset', 'ticket']
        
        for email_type in email_types:
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
