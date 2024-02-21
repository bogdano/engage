from .models import Team
from django.db.models import Sum
from django.shortcuts import render

def leaderboard(request):
    # renders the initial page
    return render(request, 'leaderboard.html')

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