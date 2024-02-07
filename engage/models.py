from django.db import models

class Todo(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

# model for activities
class Activity(models.Model):
    pass

class User(models.Model):
<<<<<<< HEAD
    pass

=======
    pass
>>>>>>> 33d4707a569d70398f24412ca11ac3a12c63fdda
