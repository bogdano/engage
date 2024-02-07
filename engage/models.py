from django.db import models


# model for activities
class Activity(models.Model):
    pass


class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(max_length=10)


class itemColor(models.Model):
    pass
