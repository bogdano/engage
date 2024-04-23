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
from cart.views import (
    add_to_cart,
    cart,
    hx_menu_cart,
    update_cart,
    hx_cart_total,
    hx_summary,
    checkout,
    clear_cart,
)
from . import views
from leaderboard.views import *

# register engage namespace
app_name = "engage"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("leaderboard/", include("leaderboard.urls")),
    path("notifications/", include("notifications.urls")),

    path("profile/<int:pk>/", views.profile, name="profile"),
    path("profile/", views.profile, name="profile"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("additional_past_activities/<int:user_id>/", views.additional_past_activities, name="additional_past_activities"),

    path("add_activity/", views.add_activity, name="add_activity"),
    path("activity/<int:pk>/", views.activity, name="activity"),
    path("new_activity/", views.new_activity, name="new_activity"),
    path("leave_activity/<int:pk>/", views.leave_activity, name="leave_activity"),
    path("bookmark_activity/<int:pk>/", views.bookmark_activity, name="bookmark_activity"),
    path("bookmark_activity_from_activity/<int:pk>/", views.bookmark_activity_from_activity, name="bookmark_activity_from_activity"),
    path("load-more-activities/", views.load_more_activities, name="load_more_activities"),
    path("award_participation_points/<int:pk>/", views.award_participation_points, name="award_participation_points"),
    path("edit_activity/<int:pk>/", views.edit_activity, name="edit_activity"),
    path("update_activity/<int:pk>/", views.update_activity, name="update_activity"),
    path("delete_activity/<int:pk>/", views.delete_activity, name="delete_activity"),
    path("approve_activity/<int:pk>/", views.approve_activity, name="approve_activity"),
    path("additional_users/<int:pk>/", views.additional_users, name="additional_users"),

    # service worker for offline PWA
    path("sw.js", views.ServiceWorker.as_view(), name="sw"),
    path("offline/", views.offline, name="offline"),

    path("store/", views.store, name="store"),
    path("new_item/", views.new_item, name="new_item"),
    path("add_item/", views.add_item, name="add_item"),
    path("item/<int:pk>/", views.item, name="item"),
    path("add_to_cart/<int:item_id>/", add_to_cart, name="add_to_cart"),
    path("cart/", cart, name="cart"),
    path("hx_menu_cart/", hx_menu_cart, name="hx_menu_cart"),
    path("update_cart/<int:item_id>/<str:action>/", update_cart, name="update_cart"),
    path("hx_cart_total/", hx_cart_total, name="hx_cart_total"),
    path("hx_summary/", hx_summary, name="hx_summary"),
    path("checkout/", checkout, name="checkout"),
    path("clear_cart/", clear_cart, name="clear_cart"),
    path("edit_item/<int:pk>/", views.edit_item, name="edit_item"),
    path("edit_item_form/<int:pk>/", views.edit_item_form, name="edit_item_form"),
    path("delete_item/<int:pk>/", views.delete_item, name="delete_item"),
]

if settings.DJANGO_ENVIRONMENT == "local":
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
