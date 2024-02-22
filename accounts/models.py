from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from django.utils import timezone

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Set the user's password
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)  # Depending on your model, you might or might not need this

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if 'is_admin' in extra_fields and extra_fields.get('is_admin') is not True:  # This check depends on your usage
            raise ValueError('Superuser must have is_admin=True.')  # Adjust based on your model's fields

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_picture = models.CharField(max_length=100, default="", blank=True)
    description = models.TextField(default="", blank=True)

    # default fields - use is_active instead of deleting, is_staff allows user to access admin interface
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # custom fields
    is_admin = models.BooleanField(default=False)
    is_on_team = models.BooleanField(default=False)
    is_teamlead = models.BooleanField(default=False)

    balance = models.IntegerField(default=0)
    lifetime_points = models.IntegerField(default=0)
    position = models.CharField(max_length=50, default="", blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.first_name + " " + self.last_name + " (" + self.email + ")"

class LoginToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True)
    # delete token after usage, or if it is accessed and expired

    def __str__(self):
        return str(self.token)

    def save(self, *args, **kwargs):
        # Set expiration_date for new records only
        if not self.pk:  # Check if the instance is new (has no primary key yet)
            self.expiration_date = timezone.now() + timezone.timedelta(minutes=15)
        super(LoginToken, self).save(*args, **kwargs)