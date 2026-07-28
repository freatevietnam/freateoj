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

    function renderNotifications(data) {
        var $body = $('#notification-dropdown .notification-dropdown-body');
        if (!data.notifications || !data.notifications.length) {
            $body.html('<div class="notification-empty">No notifications yet.</div>');
            return;
        }
        var html = '<ul class="notification-list">';
        data.notifications.forEach(function(n) {
            var unreadClass = n.read ? '' : ' unread';
            var urlAttr = n.url ? ' data-url="' + escapeHtml(n.url) + '"' : '';
            html += '<li class="notification-item' + unreadClass + '" data-id="' + n.id + '"' + urlAttr + '>' +
                '<div class="notification-title">' + escapeHtml(n.title) + '</div>';
            if (n.body) {
                html += '<div class="notification-body">' + escapeHtml(n.body) + '</div>';
            }
            html += '<div class="notification-time">' + timeAgo(n.time) + '</div>' +
                '</li>';
        });
        html += '</ul>';
        $body.html(html);
    }

    function timeAgo(isoString) {
        var now = new Date();
        var date = new Date(isoString);
        var diff = Math.floor((now - date) / 1000);
        if (diff < 60) return 'just now';
        if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
        if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
        if (diff < 2592000) return Math.floor(diff / 86400) + 'd ago';
        return date.toLocaleDateString();
    }

    function fetchNotifications() {
        var $body = $('#notification-dropdown .notification-dropdown-body');
        $body.html('<div class="notification-loading">Loading...</div>');
        $.ajax({
            url: '/notifications/ajax',
            method: 'GET',
            success: function(data) {
                renderNotifications(data);
                updateBadge(data.unread_count);
            },
            error: function() {
                $body.html('<div class="notification-empty">Failed to load notifications.</div>');
            }
        });
    }

    // Initialize
    $(function() {
        updateBadge(UNREAD_COUNT);
        initRealtime();

        // Bell click toggle dropdown
        $('#notification-bell').on('click', function(e) {
            e.preventDefault();
            var $dropdown = $('#notification-dropdown');
            if ($dropdown.is(':visible')) {
                $dropdown.hide();
            } else {
                fetchNotifications();
                $dropdown.show();
            }
        });

        // Close dropdown on click outside
        $(document).on('click', function(e) {
            if (!$(e.target).closest('.notification-wrapper').length) {
                $('#notification-dropdown').hide();
            }
        });

        // Mark all read
        $(document).on('click', '.notification-mark-all', function(e) {
            e.preventDefault();
            markRead(null);
            $('#notification-dropdown .notification-item.unread').removeClass('unread');
        });

        // Mark single read & navigate
        $(document).on('click', '.notification-item', function() {
            var $item = $(this);
            var id = $item.data('id');
            var url = $item.data('url');
            if (id && $item.hasClass('unread')) {
                markRead(id);
                $item.removeClass('unread');
            }
            if (url) {
                window.location.href = url;
            }
        });
    });

    // Expose globally
    window.notificationMarkRead = markRead;
    window.updateNotificationBadge = updateBadge;
})();
