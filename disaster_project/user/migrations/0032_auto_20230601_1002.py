# Generated by Django 3.2 on 2023-06-01 07:02

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0031_auto_20230525_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpneed',
            name='helpneedid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='helpneed',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
