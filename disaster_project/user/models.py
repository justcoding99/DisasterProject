from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    extra = models.CharField(max_length=30, blank=True)


class HelpNeed(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    address = models.TextField(null=True, blank=True)
    lat = models.CharField(max_length=255, default='0')
    lon = models.CharField(max_length=255, default='0')

    is_helped = models.BooleanField(default=False)
    helper = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
