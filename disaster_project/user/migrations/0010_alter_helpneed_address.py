# Generated by Django 3.2 on 2023-04-18 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_helpneed_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helpneed',
            name='address',
            field=models.TextField(null=True),
        ),
    ]
