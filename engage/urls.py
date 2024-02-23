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
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('accounts/', include('accounts.urls')),  # new
    path("__reload__/", include("django_browser_reload.urls")),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('leaderboard/individual/', views.individual_leaderboard, name='individual_leaderboard'),
    path('leaderboard/team/', views.team_leaderboard, name='team_leaderboard'),
    path('store/', views.store, name='store'),
]
