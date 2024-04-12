from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from engage.models import Notification

# Create your views here.
@login_required
def notifications(request):
    user_notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': user_notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = request.user.notifications.get(id=notification_id)
    notification.read = True
    notification.save()
    return redirect('notifications')
