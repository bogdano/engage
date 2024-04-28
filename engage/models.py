from django.db import models
from django.conf import settings
    
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

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.title}"

class Leaderboard(models.Model):
    leaderboard_name = models.CharField(
        max_length=200, null=False, blank=False, unique=True
    )
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
    logo = models.CharField(max_length=200, default="", blank=True)
    monthly_rank = models.IntegerField(default=0)
    description = models.TextField(default="", blank=True)
    created_on = models.DateField(auto_now_add=True, null=True)
    # team points will be calculated by summing the points of all users in the team,
    # queries by time can be done by filtering the UserParticipates model by date for the team members
    def __str__(self):
        return self.name

# stores all basic item info
class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.CharField(max_length=300)
    created_at = models.DateField(auto_now_add=True)
    image = models.CharField(max_length=200, default="", blank=True)
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
