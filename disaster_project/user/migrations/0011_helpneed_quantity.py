# Generated by Django 3.2 on 2023-04-18 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_alter_helpneed_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpneed',
            name='quantity',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
