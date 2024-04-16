from django import forms
from engage.models import Team, Leaderboard

class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class JoinTeamForm(forms.Form):
    team_id = forms.IntegerField(widget=forms.HiddenInput())

class LeaderboardForm(forms.ModelForm):
    class Meta:
        model = Leaderboard
        fields = ['leaderboard_name', 'leaderboard_logo', 'leaderboard_color']  # Include other fields as necessary