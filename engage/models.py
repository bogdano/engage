from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User


# model for activities
class Activity(models.Model):
    # title string
    title = models.CharField(max_length=200)
    # description string
    description = models.TextField()
    # creator_id foreign key to custom user model
    creator_id = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)
    # location string
    location = models.CharField(max_length=200)
    # event_date date
    event_date = models.DateField()
    # created_at date
    created_at = models.DateField(auto_now_add=True)
    # activity_type fk to activity type model
    activity_type = models.ForeignKey("ActivityType", on_delete=models.CASCADE)
    # photo field string
    photo = models.CharField(max_length=200)
    # points value
    points = models.IntegerField()


class ActivityType(models.Model):
    activity_type_name = models.CharField(max_length=200)
    activity_type_logo = models.CharField(max_length=200)


# stores all basic item info
class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.CharField(max_length=200)
    created_at = models.DateField(auto_now_add=True)


# stores all item color values
class ItemColors(models.Model):
    color = models.CharField(max_length=200)


# stores all item size values
class ItemSizes(models.Model):
    size = models.CharField(max_length=200)


# stores combinations of separate info from other item tables
class ItemVariant(models.Model):
    item_type = models.ForeignKey("Item", on_delete=models.CASCADE)
    item_color = models.ForeignKey("ItemColors", on_delete=models.CASCADE)
    item_size = models.ForeignKey("ItemSizes", on_delete=models.CASCADE)

class UserParticipated(models.Model):
    # user_id fk to custom user model
    user_id = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)
    # activity_id fk to activity model
    activity_id = models.ForeignKey("Activity", on_delete=models.CASCADE)
    # date created
    date_participated = models.DateField(auto_now_add=True)
    
class UserInterested(models.Model):
    # user_id fk to custom user model
    user_id = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    # activity_id fk to activity model
    activity_id = models.ForeignKey("Activity", on_delete=models.CASCADE)
 
class Team(models.Model):
    name = models.CharField(max_length=200)
    leader = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT, null=True, blank=True, related_name='team_leader')
    member = models.ManyToManyField('accounts.CustomUser', related_name='team_member')
    # team points will be calculated by summing the points of all users in the team, 
    # queries by time can be done by filtering the UserParticipates model by date for the team members