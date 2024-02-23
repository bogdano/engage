from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# model for activities
class Activity(models.Model):
    # title string
    title = models.CharField(max_length=200)
    # description string
    description = models.TextField()
    # creator_id foreign key to custom user model
    creator_id = models.ForeignKey("User", on_delete=models.CASCADE)
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


class ActivityType(models.Model):
    pass


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
    item_type = models.ForeignKey(
        "Item", on_delete=models.CASCADE, null=True, blank=True
    )
    item_color = models.ForeignKey(
        "ItemColors", on_delete=models.CASCADE, null=True, blank=True
    )
    item_size = models.ForeignKey(
        "ItemSizes", on_delete=models.CASCADE, null=True, blank=True
    )
    image1 = models.CharField(max_length=200)
    image2 = models.CharField(max_length=200, null=True, blank=True)
    image3 = models.CharField(max_length=200, null=True, blank=True)


class UserParticipates(models.Model):
    # user_id fk to custom user model
    user_id = models.ForeignKey("User", on_delete=models.CASCADE)
    # activity_id fk to activity model
    activity_id = models.ForeignKey("Activity", on_delete=models.CASCADE)


class UserInterested(models.Model):
    # user_id fk to custom user model
    user_id = models.ForeignKey("User", on_delete=models.CASCADE)
    # activity_id fk to activity model
    activity_id = models.ForeignKey("Activity", on_delete=models.CASCADE)


class Team(models.Model):
    name = models.CharField(max_length=200)
    leader = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="led_team", null=True, blank=True
    )

    def total_points(self):
        # Calculate the total points of all users in this team
        return (
            self.userprofile_set.aggregate(total_points=Sum("points"))["total_points"]
            or 0
        )


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
