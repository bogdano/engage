from django.contrib import admin
from engage.models import Activity, Leaderboard, UserParticipated, Team, Item, ActivityType
from .models import CustomUser, LoginToken

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date')

class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('leaderboard_name',)

class UserParticipatedAdmin(admin.ModelAdmin):
    list_display = ('activity_title', 'user_name')

    def activity_title(self, obj):
        return obj.activity.title

    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')

admin.site.register(CustomUser)
admin.site.register(LoginToken)

admin.site.register(Activity, ActivityAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
admin.site.register(UserParticipated, UserParticipatedAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ActivityType)