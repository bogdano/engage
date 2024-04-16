from engage.models import Team, Activity, Leaderboard, Item, UserParticipated, Notification
from leaderboard.forms import TeamCreateForm, JoinTeamForm, LeaderboardForm
from notifications.views import *
from accounts.models import CustomUser
from django.db.models import Sum, Count, Exists, OuterRef, Prefetch, Q
from django.db.models.functions import TruncDay
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
import cloudinary.uploader
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import dateutil.parser
from django.views.generic import TemplateView
from django.urls import reverse

def leaderboard(request):

    return render(request, "leaderboard.html")

def individual_leaderboard_view(request):
    leaderboards = Leaderboard.objects.all()
    selected_leaderboard_id = request.GET.get('leaderboard_id', None)
    date_filter = request.GET.get('date_filter', None)

    # Default to None, will be used to filter by date if specified
    start_date = None

    now = datetime.now()
    if date_filter == "this_year":
        start_date = datetime(now.year, 1, 1)
    elif date_filter == "this_month":
        start_date = datetime(now.year, now.month, 1)

    user_participations = UserParticipated.objects.all()

    if start_date:
        user_participations = user_participations.filter(date_participated__gte=start_date)

    if selected_leaderboard_id:
        user_participations = user_participations.filter(activity__leaderboards__id=selected_leaderboard_id)

    users_with_points = user_participations.values(
        'user__id', 'user__first_name', 'user__last_name'
    ).annotate(
        total_points=Sum('activity__points')
    ).order_by('-total_points')

    if request.headers.get('HX-Request', False):
        # If HTMX request, only return the necessary partial
        return render(request, "partials/individual_leaderboard.html", {
            "users_with_points": users_with_points
        })
    else:
        # Return the full page for normal requests
        return render(request, "leaderboard.html", {
            "users_with_points": users_with_points,
            "leaderboards": leaderboards,
            "selected_leaderboard_id": selected_leaderboard_id,
            "date_filter": date_filter
        })


def team_leaderboard_view(request):
    leaderboards = Leaderboard.objects.all()
    selected_leaderboard_id = request.GET.get('leaderboard_id')
    teams_query = Team.objects.prefetch_related(
        Prefetch(
            "member",
            queryset=CustomUser.objects.annotate(total_points=Sum("lifetime_points"))
        )
    )

    # Filtering by leaderboard type
    leaderboard_id = request.GET.get('leaderboard_id')
    if leaderboard_id:
        teams_query = teams_query.filter(activities__leaderboards__id=leaderboard_id)

    # Filtering by date
    date_filter = request.GET.get('date_filter')
    now = timezone.now()

    if date_filter == "this_year":
        start_of_year = datetime(now.year, 1, 1)
        start_date = timezone.make_aware(start_of_year)
    elif date_filter == "this_month":
        start_of_month = datetime(now.year, now.month, 1)
        start_date = timezone.make_aware(start_of_month)
    else:
        start_date = timezone.make_aware(datetime(1, 1, 1)) 

    end_date = now

    teams = teams_query.annotate(team_points=Sum("member__lifetime_points")).order_by("-team_points")

    return render(request, "partials/team_leaderboard.html", {
        "teams": teams,
        "leaderboards": leaderboards,
        "selected_leaderboard_id": selected_leaderboard_id,
        "date_filter": date_filter
    })


def leaderboard_view(request):
    # Determine the mode (individual or team) based on a parameter
    leaderboard_mode = request.GET.get('leaderboard_mode', 'individual')

    context = {
        'leaderboard_mode': leaderboard_mode,
        'leaderboards': Leaderboard.objects.all(),
    }

    # Logic for individual leaderboard
    if leaderboard_mode == 'individual':
        users = CustomUser.objects.annotate(total_points=Sum("lifetime_points")).order_by("-total_points")
        context['users'] = users

    # Logic for team leaderboard
    elif leaderboard_mode == 'team':
        teams = Team.objects.annotate(team_points=Sum("member__lifetime_points")).order_by("-team_points")
        context['teams'] = teams

    return render(request, "leaderboard.html", context)

def edit_leaderboard(request):
    leaderboards = Leaderboard.objects.all()
    return render(request, 'edit_leaderboard.html', {'leaderboards': leaderboards})

def edit_leaderboard_detail(request, pk):
    leaderboard = get_object_or_404(Leaderboard, pk=pk)
    if request.method == 'POST':
        form = LeaderboardForm(request.POST, instance=leaderboard)
        if form.is_valid():
            form.save()
            # Redirect to a new URL:
            return redirect('edit_leaderboard')
    else:
        form = LeaderboardForm(instance=leaderboard)
    return render(request, 'edit_leaderboard_detail.html', {'form': form, 'leaderboard': leaderboard})

def list_teams(request):
    teams = Team.objects.all()
    join_form = JoinTeamForm()
    return render(request, 'list_teams.html', {'teams': teams, 'join_form': join_form})

def create_team(request):
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.leader = request.user
            team.save()
            messages.success(request, 'Team created successfully.')
            return redirect('list_teams')
    else:
        form = TeamCreateForm()
    return render(request, 'create_team.html', {'form': form})

def join_team(request):
    if request.method == 'POST':
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            team_id = form.cleaned_data['team_id']
            team = get_object_or_404(Team, id=team_id)
            team.member.add(request.user)
            messages.success(request, 'Join request sent.')
            return redirect('list_teams')
    else:
        return redirect('list_teams')