from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

# model for activities
class Activity(models.Model):
    pass

class User(models.Model):
    pass

    pass

# model for teams
class Team(models.Model):
    name = models.CharField(max_length=200)
    leader = models.OneToOneField(User, on_delete=models.PROTECT, primary_key = True)

    def total_points(self):
        # Calculate the total points of all users in this team
        return self.userprofile_set.aggregate(total_points=Sum('points'))['total_points'] or 0
    
# model that extends User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField(default=0)
