# Generated by Django 3.2 on 2023-04-13 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_delete_helpprovider'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpneed',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
