# Generated by Django 3.2 on 2023-05-17 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0019_helpneed_original_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helpneed',
            name='is_helped',
            field=models.BooleanField(default=False, null=True),
        ),
    ]