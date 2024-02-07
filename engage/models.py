from django.db import models

class Todo(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

# model for activities
class Activity(models.Model):
    pass

class User(models.Model):
    pass

