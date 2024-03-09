"""
URL configuration for engage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.homepage, name="homepage"),
    path("accounts/", include("accounts.urls")), 

    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("leaderboard/individual/", views.individual_leaderboard, name="individual_leaderboard"),
    path("leaderboard/team/", views.team_leaderboard, name="team_leaderboard"),

    path("store/", views.store, name="store"),
    path("notifications/", views.notifications, name="notifications"),
    path("profile/", views.profile, name="profile"),
    path("edit_profile", views.edit_profile, name="edit_profile"),

    path("add_activity/", views.add_activity, name="add_activity"),
    path("activity/<int:pk>/", views.activity, name="activity"),
    path("new_activity/", views.new_activity, name="new_activity"),
    path("bookmark_activity/<int:pk>/", views.bookmark_activity, name="bookmark_activity"),
    path("bookmark_activity_from_activity/<int:pk>/", views.bookmark_activity_from_activity, name="bookmark_activity_from_activity"),
    path('load-more-activities/', views.load_more_activities, name='load_more_activities'),
    path('award_participation_points/<int:pk>/', views.award_participation_points, name='award_participation_points'),

    path("new_item/", views.new_item, name="new_item"),
    path("add_item/", views.add_item, name="add_item"),
    path("item/<int:pk>/", views.item, name="item"),

    # path('', include('pwa.urls')),
]

if settings.DEBUG:
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]

