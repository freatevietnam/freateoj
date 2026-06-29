import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from judge.models.notification import Notification
from judge.utils.cache_helper import unread_notification_count_cache_factory


@method_decorator(login_required, name='dispatch')
class NotificationList(View):
    def get(self, request, *args, **kwargs):
        notifications = request.profile.notifications.all()[:50]
        return render(request, 'notification/list.html', {
            'title': 'Notifications',
            'notifications': notifications,
        })


@method_decorator(login_required, name='dispatch')
class NotificationAjax(View):
    def get(self, request, *args, **kwargs):
        notifications = request.profile.notifications.all()[:20]
        data = [{
            'id': n.id,
            'title': n.title,
            'body': n.body,
            'url': n.url,
            'time': n.time.isoformat(),
            'read': n.read,
        } for n in notifications]
        return JsonResponse({'notifications': data, 'unread_count': request.profile.unread_notification_count})


@method_decorator(login_required, name='dispatch')
class NotificationMarkRead(View):
    def post(self, request, *args, **kwargs):
        if request.POST.get('all'):
            request.profile.notifications.filter(read=False).update(read=True)
        else:
            try:
                notification = request.profile.notifications.get(id=request.POST['id'])
                notification.read = request.POST.get('read', '1') == '1'
                notification.save(update_fields=['read'])
            except (Notification.DoesNotExist, KeyError):
                pass

        factory = unread_notification_count_cache_factory(request.profile.id)
        count = request.profile.notifications.filter(read=False).count()
        factory.set_cache(count)
        return JsonResponse({'unread_count': count})
