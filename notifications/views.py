from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from engage.models import Notification

# Create your views here.
def notifications(request):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    user_notifications = request.user.notifications.all().order_by('-created_at')
    # mark all notifications as read
    user_notifications.update(read=True)
    return render(request, 'notifications.html', {'notifications': user_notifications})

def dismiss_notification(request, notification_id):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    notification = get_object_or_404(Notification, id=notification_id)
    notification.delete()
    return redirect('notifications')