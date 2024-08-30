from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Vendor(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    availablePages = models.IntegerField(name="AvailablePages", default=0)
    tonerCount = models.IntegerField(name="TonerCount", default=0)
    drumCount = models.IntegerField(name="DrumCount", default=0)
