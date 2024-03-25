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
from cart.views import add_to_cart, cart, hx_menu_cart, update_cart, hx_cart_total
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("leaderboard/individual/", views.individual_leaderboard_view, name="individual_leaderboard"),
    path("leaderboard/team/", views.team_leaderboard_view, name="team_leaderboard"),
    path("store/", views.store, name="store"),
    path("notifications/", views.notifications, name="notifications"),
    path("profile/", views.profile, name="profile"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("add_activity/", views.add_activity, name="add_activity"),
    path("activity/<int:pk>/", views.activity, name="activity"),
    path("new_activity/", views.new_activity, name="new_activity"),
    path(
        "bookmark_activity/<int:pk>/", views.bookmark_activity, name="bookmark_activity"
    ),
    path(
        "bookmark_activity_from_activity/<int:pk>/",
        views.bookmark_activity_from_activity,
        name="bookmark_activity_from_activity",
    ),
    path(
        "load-more-activities/", views.load_more_activities, name="load_more_activities"
    ),
    path(
        "award_participation_points/<int:pk>/",
        views.award_participation_points,
        name="award_participation_points",
    ),
    path("additional_users/<int:pk>/", views.additional_users, name="additional_users"),
    # service worker for offline PWA
    # path('sw.js', views.ServiceWorker.as_view(), name="sw"),
    path("new_item/", views.new_item, name="new_item"),
    path("add_item/", views.add_item, name="add_item"),
    path("item/<int:pk>/", views.item, name="item"),
    path("add_to_cart/<int:item_id>/", add_to_cart, name="add_to_cart"),
    path("cart/", cart, name="cart"),
    path("hx_menu_cart/", hx_menu_cart, name="hx_menu_cart"),
    path("update_cart/<int:item_id>/<str:action>/", update_cart, name="update_cart"),
    path("hx_cart_total/", hx_cart_total, name="hx_cart_total"),
    # path('', include('pwa.urls')),
]

if settings.DJANGO_ENVIRONMENT == "local":
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
