from engage.models import Team, Leaderboard, UserParticipated
from leaderboard.forms import TeamCreateForm, JoinTeamForm, LeaderboardForm
from notifications.views import *
from django.db.models import Sum, Q
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
import cloudinary.uploader
from datetime import datetime
from django.contrib import messages

def leaderboard(request):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    leaderboard_mode = request.GET.get('leaderboard_mode', 'individual')
    selected_leaderboard_id = request.GET.get('leaderboard_id', None)
    date_filter = request.GET.get('date_filter', 'this_month')

    leaderboards = Leaderboard.objects.all()
    now = timezone.now()
    start_date = datetime(now.year, now.month, 1) if date_filter == "this_month" else datetime(now.year, 1, 1)
    context = {
        'leaderboard_mode': leaderboard_mode,
        'leaderboards': leaderboards,
        'selected_leaderboard_id': selected_leaderboard_id,
        'date_filter': date_filter,
    }

    if leaderboard_mode == 'individual':
        user_participations = UserParticipated.objects.filter(date_participated__gte=start_date)
        if selected_leaderboard_id:
            user_participations = user_participations.filter(activity__leaderboards__id=selected_leaderboard_id)
        if start_date:
            start_date = timezone.make_aware(start_date)
            user_participations = user_participations.filter(date_participated__gte=start_date)

        users = user_participations.values(
            'user__id', 'user__first_name', 'user__last_name'
        ).annotate(
            total_points=Sum('activity__points')
        ).order_by('-total_points')
        context['users'] = users

    elif leaderboard_mode == 'team':
        if start_date:
            start_date = timezone.make_aware(start_date)  # Ensure the datetime is timezone aware
            user_participations = UserParticipated.objects.filter(date_participated__gte=start_date)
        else:
            user_participations = UserParticipated.objects.all()  # No date filtering for 'all time'

        if selected_leaderboard_id:
            user_participations = user_participations.filter(activity__leaderboards__id=selected_leaderboard_id)

        # Simplify the aggregation of points
        teams = Team.objects.annotate(
            team_points=Sum('member__userparticipated__activity__points', filter=Q(member__userparticipated__in=user_participations))
        ).filter(team_points__gt=0).order_by('-team_points')       
        context['teams'] = teams

    return render(request, "leaderboard.html", context)


def edit_leaderboard(request):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    leaderboards = Leaderboard.objects.all()
    return render(request, 'edit_leaderboard.html', {'leaderboards': leaderboards})


def edit_leaderboard_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
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
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    teams = Team.objects.all()
    for team in teams:
        team.is_member = request.user in team.member.all()
    join_form = JoinTeamForm()
    return render(request, 'list_teams.html', {'teams': teams, 'join_form': join_form})


def create_team(request):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.leader = request.user
            team.save()
            team.member.add(request.user)  # Auto-add the creator as a member
            messages.success(request, 'Team created successfully.')
            return redirect('list_teams')
    else:
        form = TeamCreateForm()
    return render(request, 'create_team.html', {'form': form})


def join_team(request):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    if request.method == 'POST':
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            team_id = form.cleaned_data['team_id']
            team = get_object_or_404(Team, id=team_id)
            # Check if the user is already in a team
            if not request.user.team_member.exists():
                team.member.add(request.user)
                messages.success(request, 'You have joined the team.')
            else:
                messages.error(request, 'You are already in a team.')
            return redirect('list_teams')
    else:
        return redirect('list_teams')
    

def leave_team(request, team_id):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    if request.method == 'POST':
        team = get_object_or_404(Team, id=team_id)
        # Check if the user is a member of the team
        if request.user in team.member.all():
            team.member.remove(request.user)
            messages.success(request, 'You have left the team.')
        else:
            messages.error(request, 'You are not a member of this team.')
        return redirect('list_teams')
    else:
        return redirect('list_teams')
    

def team_detail(request, team_id):
    if not request.user.is_authenticated:
        return redirect('send-login-link')
    team = Team.objects.get(id=team_id)
    return render(request, 'team_detail.html', {'team': team})

