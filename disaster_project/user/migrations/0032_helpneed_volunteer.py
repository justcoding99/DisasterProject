# Generated by Django 3.2 on 2023-05-28 19:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0031_auto_20230525_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpneed',
            name='volunteer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
