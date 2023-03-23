from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    extra = models.CharField(max_length=30, blank=True)


class HelpNeed(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# --------------- Rawan -------------------

Volunteer_Field = (
    ('food','Provide Food'),
    ('transportation', 'Provide Transportation'),
    ('shelter','Provide Shelter'),
)
class Volunteer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    volunteer_field = models.CharField(max_length=15, choices=Volunteer_Field)

    def __str__(self):
        return self.name