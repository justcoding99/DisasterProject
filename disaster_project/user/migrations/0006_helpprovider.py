# Generated by Django 3.2 on 2023-04-13 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_delete_helpprovider'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=255)),
                ('password', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=255)),
            ],
        ),
    ]
