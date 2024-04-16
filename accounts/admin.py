from django.contrib import admin
from engage.models import Activity, Leaderboard, UserParticipated, Team, Item, Notification
from .models import CustomUser, LoginToken

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'is_active')

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

# display logintoken with user email and date/time of creation
class LoginTokenAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'date_created', 'token')
    def user_email(self, obj):
        return obj.user.email
    
# display customusers with user.str, date joined, balance, and whether they are a superuser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user_str', 'date_joined', 'balance', 'is_superuser')
    def user_str(self, obj):
        return obj.__str__()

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(LoginToken, LoginTokenAdmin)

admin.site.register(Activity, ActivityAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
admin.site.register(UserParticipated, UserParticipatedAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Notification)