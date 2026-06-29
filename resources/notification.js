// Notification system - Socket.IO based
(function() {
    'use strict';

    var NOTIFICATION_SECRET = window.NOTIFICATION_SECRET || null;
    var UNREAD_COUNT = window.UNREAD_NOTIFICATION_COUNT || 0;
    var notificationSocket = null;

    function updateBadge(count) {
        UNREAD_COUNT = count;
        var badge = document.getElementById('notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    function showNotificationPopup(title, body, url) {
        // Create a simple toast notification
        var toast = document.createElement('div');
        toast.className = 'notification-toast';
        toast.innerHTML = '<strong>' + escapeHtml(title) + '</strong>' +
            (body ? '<br><small>' + escapeHtml(body) + '</small>' : '');
        if (url) {
            toast.style.cursor = 'pointer';
            toast.addEventListener('click', function() {
                window.location.href = url;
            });
        }
        document.body.appendChild(toast);
        setTimeout(function() { toast.classList.add('show'); }, 10);
        setTimeout(function() {
            toast.classList.remove('show');
            setTimeout(function() { toast.remove(); }, 300);
        }, 5000);
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    function markRead(id) {
        $.ajax({
            url: '/notifications/mark_read',
            method: 'POST',
            data: id ? {id: id} : {all: '1'},
            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || $('input[name=csrfmiddlewaretoken]').val()},
            success: function(data) {
                updateBadge(data.unread_count);
                if (!id) {
                    $('.notification-item.unread').removeClass('unread');
                } else {
                    $('#notification-' + id).removeClass('unread');
                }
            }
        });
    }

    function initRealtime() {
        if (!NOTIFICATION_SECRET || typeof io === 'undefined') return;

        try {
            var EVENT_DAEMON_GET = window.EVENT_DAEMON_GET || '';
            if (!EVENT_DAEMON_GET) return;

            notificationSocket = io(EVENT_DAEMON_GET, {
                path: '/socket.io',
                transports: ['websocket', 'polling']
            });

            notificationSocket.on('connect', function() {
                notificationSocket.emit('join', 'notification_' + NOTIFICATION_SECRET);
            });

            notificationSocket.on('notification', function(data) {
                updateBadge(UNREAD_COUNT + 1);
                UNREAD_COUNT++;
                if (data.popup) {
                    showNotificationPopup(data.title, data.body, data.url);
                }
            });
        } catch(e) {
            console.error('Notification socket error:', e);
        }
    }

    // Initialize
    $(function() {
        updateBadge(UNREAD_COUNT);
        initRealtime();

        // Mark all read button
        $(document).on('click', '.mark-all-read', function(e) {
            e.preventDefault();
            markRead(null);
        });

        // Mark single read
        $(document).on('click', '.notification-item.unread', function() {
            var id = $(this).data('id');
            if (id) markRead(id);
        });
    });

    // Expose globally
    window.notificationMarkRead = markRead;
    window.updateNotificationBadge = updateBadge;
})();
