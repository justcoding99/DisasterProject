# Generated by Django 3.2 on 2023-06-06 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0033_hospitals'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospitals',
            name='phone',
            field=models.CharField(max_length=55),
        ),
    ]
