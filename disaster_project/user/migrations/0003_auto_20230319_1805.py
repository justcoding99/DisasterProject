# Generated by Django 3.2 on 2023-03-19 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_helpneed'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpneed',
            name='lat',
            field=models.CharField(default='0', max_length=255),
        ),
        migrations.AddField(
            model_name='helpneed',
            name='lon',
            field=models.CharField(default='0', max_length=255),
        ),
        migrations.AlterField(
            model_name='helpneed',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
