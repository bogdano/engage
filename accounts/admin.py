from django.contrib import admin
from engage.models import Activity, Leaderboard, Team, Item, Notification, UserParticipated
from .models import CustomUser, LoginToken

class UserParticipatedInline(admin.TabularInline):
    model = UserParticipated
    extra = 0  # Number of extra forms to display
    fields = ('user', 'date_participated')  # Specify which fields to include
    readonly_fields = ('date_participated',)  # Make date_participated read-only if desired

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'is_active')
    inlines = [UserParticipatedInline]

class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('leaderboard_name',)

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
admin.site.register(Team, TeamAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Notification)