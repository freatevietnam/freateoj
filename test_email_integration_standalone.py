#!/usr/bin/env python3
"""
Standalone integration tests for email progress and notification system.
This script can be run without the full Django environment.
"""
import sys
import os
from unittest.mock import patch, MagicMock, call
from datetime import datetime

# Mock Django modules before importing our code
sys.modules['django'] = MagicMock()
sys.modules['django.conf'] = MagicMock()
sys.modules['django.core'] = MagicMock()
sys.modules['django.core.cache'] = MagicMock()
sys.modules['django.contrib'] = MagicMock()
sys.modules['django.contrib.auth'] = MagicMock()
sys.modules['django.contrib.auth.models'] = MagicMock()
sys.modules['django.http'] = MagicMock()
sys.modules['django.views'] = MagicMock()
sys.modules['django.views.decorators'] = MagicMock()
sys.modules['django.views.decorators.http'] = MagicMock()
sys.modules['django.template'] = MagicMock()
sys.modules['django.template.loader'] = MagicMock()
sys.modules['celery'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Mock settings
mock_settings = MagicMock()
mock_settings.EMAIL_RATE_LIMITS = {
    'registration': {'count': 3, 'window': 300},
    'resend_verification': {'count': 3, 'window': 300},
    'password_reset': {'count': 5, 'window': 300},
    'ticket': {'count': 10, 'window': 60},
}
mock_settings.EMAIL_SEND_TIMEOUT = 60
mock_settings.EVENT_DAEMON_USE = True
mock_settings.EVENT_DAEMON_POST = 'http://localhost:9996/'
mock_settings.SITE_NAME = 'TestSite'
mock_settings.DEFAULT_FROM_EMAIL = 'noreply@test.com'

# Patch the settings module
sys.modules['django.conf'].settings = mock_settings

# Now import our modules
from judge.utils.rate_limit import EmailRateLimiter
from judge.utils.socket_events import emit_email_event


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def __init__(self):
        self.test_count = 0
        self.passed = 0
        self.failed = 0
    
    def test_rate_limiter_allows_requests_within_limit(self):
        self.test_count += 1
        print("Test: Rate limiter allows requests within limit")
        
        # Test the logic directly without mocking cache behavior
        # The rate limiter should allow requests when count < limit
        mock_cache = MagicMock()
        
        with patch('judge.utils.rate_limit.cache', mock_cache):
            limiter = EmailRateLimiter('registration')
            
            # Test case 1: When count is 0 (first request), should be allowed
            mock_cache.get.return_value = 0
            allowed, remaining = limiter.is_allowed(1)
            if not allowed:
                print("  FAIL: First request should be allowed")
                self.failed += 1
                return
            if remaining != 2:  # 3 - 0 - 1 = 2
                print(f"  FAIL: Expected remaining 2, got {remaining}")
                self.failed += 1
                return
            
            # Test case 2: When count is 1, should be allowed
            mock_cache.get.return_value = 1
            allowed, remaining = limiter.is_allowed(1)
            if not allowed:
                print("  FAIL: Second request should be allowed")
                self.failed += 1
                return
            if remaining != 1:  # 3 - 1 - 1 = 1
                print(f"  FAIL: Expected remaining 1, got {remaining}")
                self.failed += 1
                return
            
            # Test case 3: When count is 2, should be allowed
            mock_cache.get.return_value = 2
            allowed, remaining = limiter.is_allowed(1)
            if not allowed:
                print("  FAIL: Third request should be allowed")
                self.failed += 1
                return
            if remaining != 0:  # 3 - 2 - 1 = 0
                print(f"  FAIL: Expected remaining 0, got {remaining}")
                self.failed += 1
                return
            
            # Test case 4: When count is 3 (at limit), should be denied
            mock_cache.get.return_value = 3
            allowed, remaining = limiter.is_allowed(1)
            if allowed:
                print("  FAIL: Fourth request should be denied")
                self.failed += 1
                return
            
            print("  PASS")
            self.passed += 1
    
    def test_rate_limiter_different_users_independent(self):
        self.test_count += 1
        print("Test: Rate limiter different users independent")
        
        mock_cache = MagicMock()
        mock_cache.get.return_value = 0
        
        with patch('judge.utils.rate_limit.cache', mock_cache):
            limiter = EmailRateLimiter('registration')
            
            # User 1 uses all requests
            for i in range(3):
                limiter.is_allowed(1)
            
            # User 2 should still have requests
            mock_cache.get.return_value = 0
            allowed, remaining = limiter.is_allowed(2)
            
            if not allowed:
                print("  FAIL: User 2 should have requests available")
                self.failed += 1
                return
            
            if remaining != 2:
                print(f"  FAIL: Expected remaining 2, got {remaining}")
                self.failed += 1
                return
            
            print("  PASS")
            self.passed += 1
    
    def test_rate_limiter_different_email_types_independent(self):
        self.test_count += 1
        print("Test: Rate limiter different email types independent")
        
        mock_cache = MagicMock()
        mock_cache.get.return_value = 0
        
        with patch('judge.utils.rate_limit.cache', mock_cache):
            limiter_reg = EmailRateLimiter('registration')
            limiter_ticket = EmailRateLimiter('ticket')
            
            # Use all registration requests
            for i in range(3):
                limiter_reg.is_allowed(1)
            
            # Ticket requests should still work
            mock_cache.get.return_value = 0
            allowed, remaining = limiter_ticket.is_allowed(1)
            
            if not allowed:
                print("  FAIL: Ticket requests should still work")
                self.failed += 1
                return
            
            if remaining != 9:
                print(f"  FAIL: Expected remaining 9, got {remaining}")
                self.failed += 1
                return
            
            print("  PASS")
            self.passed += 1
    
    def test_rate_limiter_get_remaining_does_not_increment(self):
        self.test_count += 1
        print("Test: Rate limiter get_remaining does not increment")
        
        mock_cache = MagicMock()
        mock_cache.get.return_value = 0
        
        with patch('judge.utils.rate_limit.cache', mock_cache):
            limiter = EmailRateLimiter('registration')
            
            # Check remaining without incrementing
            remaining = limiter.get_remaining(1)
            if remaining != 3:
                print(f"  FAIL: Expected remaining 3, got {remaining}")
                self.failed += 1
                return
            
            # Check again - should still be 3
            remaining = limiter.get_remaining(1)
            if remaining != 3:
                print(f"  FAIL: Expected remaining 3, got {remaining}")
                self.failed += 1
                return
            
            # Now increment
            limiter.is_allowed(1)
            
            # Check remaining - should be 2
            mock_cache.get.return_value = 1
            remaining = limiter.get_remaining(1)
            if remaining != 2:
                print(f"  FAIL: Expected remaining 2, got {remaining}")
                self.failed += 1
                return
            
            print("  PASS")
            self.passed += 1
    
    def run_all(self):
        print("\n=== Rate Limiter Tests ===")
        self.test_rate_limiter_allows_requests_within_limit()
        self.test_rate_limiter_different_users_independent()
        self.test_rate_limiter_different_email_types_independent()
        self.test_rate_limiter_get_remaining_does_not_increment()
        print(f"\nRate Limiter Tests: {self.passed}/{self.test_count} passed")


class TestSocketIOEvents:
    """Test Socket.IO event emission."""
    
    def __init__(self):
        self.test_count = 0
        self.passed = 0
        self.failed = 0
    
    def test_emit_email_event_success(self):
        self.test_count += 1
        print("Test: Emit email event success")
        
        mock_requests = MagicMock()
        mock_requests.post.return_value = MagicMock(status_code=200)
        
        with patch('judge.utils.socket_events.requests', mock_requests):
            emit_email_event('task-123', 'progress', {'progress': 50})
            
            if not mock_requests.post.called:
                print("  FAIL: POST request was not made")
                self.failed += 1
                return
            
            call_args = mock_requests.post.call_args
            if call_args[0][0] != 'http://localhost:9996/':
                print(f"  FAIL: Wrong URL: {call_args[0][0]}")
                self.failed += 1
                return
            
            json_data = call_args[1]['json']
            if json_data['command'] != 'post':
                print(f"  FAIL: Wrong command: {json_data['command']}")
                self.failed += 1
                return
            
            if json_data['channel'] != 'email:task-123':
                print(f"  FAIL: Wrong channel: {json_data['channel']}")
                self.failed += 1
                return
            
            if json_data['message']['type'] != 'email_progress':
                print(f"  FAIL: Wrong message type: {json_data['message']['type']}")
                self.failed += 1
                return
            
            print("  PASS")
            self.passed += 1
    
    def test_emit_email_event_error(self):
        self.test_count += 1
        print("Test: Emit email event error")
        
        mock_requests = MagicMock()
        mock_requests.post.return_value = MagicMock(status_code=200)
        
        with patch('judge.utils.socket_events.requests', mock_requests):
            emit_email_event('task-456', 'error', {'error': 'Something went wrong'})
            
            if not mock_requests.post.called:
                print("  FAIL: POST request was not made")
                self.failed += 1
                return
            
            call_args = mock_requests.post.call_args
            json_data = call_args[1]['json']
            
            if json_data['message']['type'] != 'email_error':
                print(f"  FAIL: Wrong message type: {json_data['message']['type']}")
                self.failed += 1
                return
            
            if json_data['message']['error'] != 'Something went wrong':
                print(f"  FAIL: Wrong error message: {json_data['message']['error']}")
                self.failed += 1
                return
            
            print("  PASS")
            self.passed += 1
    
    def test_emit_email_event_disabled(self):
        self.test_count += 1
        print("Test: Emit email event disabled")
        
        mock_requests = MagicMock()
        
        with patch('judge.utils.socket_events.requests', mock_requests):
            with patch('judge.utils.socket_events.settings') as mock_settings:
                mock_settings.EVENT_DAEMON_USE = False
                emit_email_event('task-999', 'progress', {'progress': 10})
                
                if mock_requests.post.called:
                    print("  FAIL: POST request was made when daemon is disabled")
                    self.failed += 1
                    return
                
                print("  PASS")
                self.passed += 1
    
    def test_emit_email_event_handles_exception(self):
        self.test_count += 1
        print("Test: Emit email event handles exception")
        
        mock_requests = MagicMock()
        mock_requests.post.side_effect = Exception('Connection refused')
        
        with patch('judge.utils.socket_events.requests', mock_requests):
            # Should not raise exception
            try:
                emit_email_event('task-101', 'progress', {'progress': 10})
            except Exception as e:
                print(f"  FAIL: Exception was raised: {e}")
                self.failed += 1
                return
            
            if not mock_requests.post.called:
                print("  FAIL: POST request was not attempted")
                self.failed += 1
                return
            
            print("  PASS")
            self.passed += 1
    
    def run_all(self):
        print("\n=== Socket.IO Event Tests ===")
        self.test_emit_email_event_success()
        self.test_emit_email_event_error()
        self.test_emit_email_event_disabled()
        self.test_emit_email_event_handles_exception()
        print(f"\nSocket.IO Event Tests: {self.passed}/{self.test_count} passed")


def main():
    print("Email Integration Tests")
    print("=" * 50)
    
    rate_limiter_tests = TestRateLimiter()
    rate_limiter_tests.run_all()
    
    socket_io_tests = TestSocketIOEvents()
    socket_io_tests.run_all()
    
    total_tests = rate_limiter_tests.test_count + socket_io_tests.test_count
    total_passed = rate_limiter_tests.passed + socket_io_tests.passed
    total_failed = rate_limiter_tests.failed + socket_io_tests.failed
    
    print("\n" + "=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    
    if total_failed > 0:
        print("\nSome tests failed!")
        return 1
    else:
        print("\nAll tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
