from django.contrib import admin
from .models import CustomUser, LoginToken

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(LoginToken)


