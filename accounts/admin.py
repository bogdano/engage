from django.contrib import admin
from .models import CustomUser, LoginToken
# import models from engage app
from engage.models import Activity, Leaderboard, UserParticipated, UserInterested, Team

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(LoginToken)
admin.site.register(Team)

# register engage models
admin.site.register(Activity)
admin.site.register(Leaderboard)
admin.site.register(UserParticipated)
admin.site.register(UserInterested)



