from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from djongo import models
import uuid



class User(AbstractUser):
    extra = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)


Help_Class = (
    ('food','Food'),
    ('shelter','Shelter'),
    ('heating','Heating'),
    ('clothes','Clothes'),
    ('medical_supplies','Medical Supplies'),
    ('hygiene','Hygiene Kits'),
)
User_Type = (
    ('victim','Victim'),
    ('volunteer','Volunteer'),
)

class HelpNeed(models.Model):
    helpneedid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=255, blank=False, null=True)
    last_name = models.CharField(max_length=255, blank=False, null=True )
    phone = models.CharField(max_length=30)
    address = models.TextField(null=True, blank=False)
    lat = models.CharField(max_length=255, default='0')
    lon = models.CharField(max_length=255, default='0')
    description = models.CharField(max_length=255, blank=False, null=True)

    is_helped = models.BooleanField(default=False)
    helpers = models.ManyToManyField(User, through='HelpNeedHelper')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quantity = models.PositiveIntegerField(default=1, blank=False, null=True)
    original_quantity = models.PositiveIntegerField(editable=False, blank=False, null=True)
    help_class = models.CharField(max_length=20, choices=Help_Class, blank=False, null=True)
    user_type = models.CharField(max_length=20, choices=User_Type, blank=False, null=True)

    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='volunteer_requests', blank=False, null=True)
    hidden = models.BooleanField(default=False)


    def __str__(self):
        return self.first_name + " " + self.last_name

    def clean(self):
        if self.quantity == 0:
            raise ValidationError("Quantity cannot be zero.")

    def save(self, *args, **kwargs):
        if not self.original_quantity:
            self.original_quantity = self.quantity
        super().save(*args, **kwargs)



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
        return self.first_name + " " + self.last_name


clothes_category = (
    ('overalls','Overalls'),
    ('tops','Tops'),
    ('bottoms', 'Bottoms'),
    ('outwear','Outwears'),
    ('underwears', 'Underwears'),
)

sizes = (
    ('newborns', 'Age 0-1 '),
    ('babies','Age 1-5'),
    ('kids', 'Age 5-10'),
    ('xs', 'XS'),
    ('s', 'S'),
    ('m', 'M'),
    ('l', 'L'),
    ('xl', 'XL'),
    ('xxl', 'XXL'),
    ('xxxl', 'XXXL'),
)
class ClothesRequest(HelpNeed):
    category = models.CharField(max_length=50, choices=clothes_category)
    size = models.CharField(max_length=50, choices=sizes)

class HelpNeedHelper(models.Model):
    help_need = models.ForeignKey(HelpNeed, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.help_need}"

    class Meta:
        unique_together = ('help_need', 'user')
