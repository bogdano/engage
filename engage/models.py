from django.db import models

class ActivityType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
# model for activities
class Activity(models.Model):
    # title string
    title = models.CharField(max_length=200, null=False, blank=False)
    # description string
    description = models.TextField()
    # creator_id foreign key to custom user model
    creator = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)
    # location details
    address = models.CharField(max_length=200)
    # latitude and longitude
    latitude = models.FloatField()
    longitude = models.FloatField()
    # event_date date
    event_date = models.DateTimeField()
    # end_date date
    end_date = models.DateTimeField()
    # created_at date
    created_at = models.DateField(auto_now_add=True)
    # photo field string
    photo = models.CharField(max_length=100, default="", blank=True)
    # points value
    points = models.IntegerField()
    # is_active boolean
    is_active = models.BooleanField(default=True)
    # is approved or not, used for mods to see activities suggested by regular users
    is_approved = models.BooleanField(default=False)
    # send alert or not boolean (only staff can do this), also place on top of feed, highlighted
    alert = models.BooleanField(default=False)
    # activity type
    activity_type = models.ForeignKey(ActivityType, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    leaderboards = models.ManyToManyField("Leaderboard", related_name="leaderboards", blank=True)
    # interested users
    interested_users = models.ManyToManyField("accounts.CustomUser", related_name="interested_users", blank=True)
    # participated users, new field for tracking participation
    participated_users = models.ManyToManyField(
        "accounts.CustomUser", 
        through='UserParticipated', 
        related_name="participated_activities", 
        blank=True
    )
    def __str__(self):
        return self.title


# so, for leaderboard queries, suppose you want to get the top 10 earners on the
# Tabletennis leaderboard in the last week you would do something like this:
# query UserParticipated for all users who participated in activities which contribute to
# said leaderboard (query the many-many field), then query those activities for each user, to
# sum the point values of each activity
# finally, order by sum total of points in that result
# also, to display a UI for picking which leaderboard to view, you can just query the
# Leaderboard model. any time someone creates an event with a previouly non-existing
# leaderboard, it will be added to the Leaderboard model (will have to add a form somewhere to set logo and color values)


class Leaderboard(models.Model):
    leaderboard_name = models.CharField(
        max_length=200, null=False, blank=False, unique=True
    )
    leaderboard_logo = models.CharField(max_length=200)
    leaderboard_color = models.CharField(max_length=200)
    def __str__(self):
        return self.leaderboard_name


class UserParticipated(models.Model):
    # user_id fk to custom user model
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)  # Renamed for clarity
    activity = models.ForeignKey("Activity", on_delete=models.CASCADE)  # Renamed for clarity
    date_participated = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        date_str = self.date_participated.strftime("%B %d, %I:%M%p")  # Example: "March 04, 2024"
        return f"{self.user.first_name} {self.user.last_name} participated in {self.activity.title} on {date_str}"



class Team(models.Model):
    name = models.CharField(max_length=200)
    leader = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="team_leader",
    )
    member = models.ManyToManyField("accounts.CustomUser", related_name="team_member")
    # team points will be calculated by summing the points of all users in the team,
    # queries by time can be done by filtering the UserParticipates model by date for the team members
    def __str__(self):
        return self.name

# stores all basic item info
class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.CharField(max_length=200)
    created_at = models.DateField(auto_now_add=True)
    image = models.CharField(max_length=100, default="", blank=True)
    def __str__(self):
        return self.name


# stores all item color values
class ItemColors(models.Model):
    color = models.CharField(max_length=200)


# stores all item size values
class ItemSizes(models.Model):
    size = models.CharField(max_length=200)


# stores combinations of separate info from other item tables
class ItemVariant(models.Model):
    item_type = models.ForeignKey("Item", on_delete=models.CASCADE)
    item_size = models.ForeignKey("ItemSizes", on_delete=models.CASCADE)
