from django import forms
from engage.models import Team, Leaderboard

class JoinTeamForm(forms.Form):
    team_id = forms.IntegerField(widget=forms.HiddenInput())