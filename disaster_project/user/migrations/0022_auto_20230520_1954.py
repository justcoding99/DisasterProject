# Generated by Django 3.2 on 2023-05-20 16:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_alter_helpneed_is_helped'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='helpneed',
            name='helper',
        ),
        migrations.AddField(
            model_name='helpneed',
            name='helpers',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
