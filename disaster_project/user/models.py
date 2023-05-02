from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


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
    first_name = models.CharField(max_length=255, blank=False, null=True)
    last_name = models.CharField(max_length=255, blank=False, null=True )
    phone = models.CharField(max_length=30)
    address = models.TextField(null=True, blank=False)
    lat = models.CharField(max_length=255, default='0')
    lon = models.CharField(max_length=255, default='0')
    description = models.CharField(max_length=255, blank=False, null=True)

    is_helped = models.BooleanField(default=False)
    helper = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    quantity = models.IntegerField(default=0, blank=False, null=True)
    help_class = models.CharField(max_length=20, choices=Help_Class, blank=False, null=True)
    user_type = models.CharField(max_length=20, choices=User_Type, blank=False, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


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
        return self.first_name + " " + self.last_name


clothes_category = (
    ('overalls','Overalls'),
    ('tops','Tops'),
    ('bottoms', 'Bottoms'),
    ('outwear','Outwears'),
    ('underwears', 'Underwears'),
)

sizes = (
    ('newborns', '0-1'),
    ('babies','1-5'),
    ('kids', '5-10'),
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
