from .models import Team, CustomUser, Activity
from accounts.models import CustomUser
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.dateparse import parse_date

def homepage(request):
    if not request.user.is_authenticated:
        return render(request, 'auth/send_login_link.html')
    else:
        return render(request, 'home.html')

def leaderboard(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date_parsed = parse_date(start_date) if start_date else None
    end_date_parsed = parse_date(end_date) if end_date else None

    queryset = Activity.objects.all()

    if start_date_parsed:
        queryset = queryset.filter(date_completed__gte=start_date_parsed)
    if end_date_parsed:
        queryset = queryset.filter(date_completed__lte=end_date_parsed)

    leaderboard_data = queryset.values('user__id', 'user__email').annotate(total_points=Sum('points')).order_by('-total_points')

    data = list(leaderboard_data)
    return JsonResponse(data, safe=False)

def individual_leaderboard(request):
    # Fetch users and their points
    users = UserProfile.objects.annotate(total_points=Sum('points')).order_by('-total_points')
    return render(request, 'partials/individual_leaderboard.html', {'users': users})

def team_leaderboard(request):
    # Fetch teams and their points
    teams = Team.objects.annotate(total_points=Sum('userprofile__points')).order_by('-total_points')
    return render(request, 'partials/team_leaderboard.html', {'teams': teams})

def leaderboard_view(request):
    # Fetch the top 10 users by points
    top_users = UserProfile.objects.order_by('-points')[:10]
    return render(request, 'partials/leaderboard_partial.html', {'top_users': top_users})

def store(request):
    return render(request, 'store.html')