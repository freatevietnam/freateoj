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
        
        socket.off('email_progress');
        socket.off('email_success');
        socket.off('email_error');
        
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
    
    // Set timeout from Django settings
    window.EMAIL_SEND_TIMEOUT = window.EMAIL_SEND_TIMEOUT || 60;
})();