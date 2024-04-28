from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.notifications, name="notifications"),
    path("dismiss/<int:notification_id>/", views.dismiss_notification, name="dismiss_notification"),
]