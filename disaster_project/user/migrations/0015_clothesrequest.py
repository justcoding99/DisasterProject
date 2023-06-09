# Generated by Django 3.2 on 2023-04-26 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_auto_20230425_2142'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClothesRequest',
            fields=[
                ('helpneed_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='user.helpneed')),
                ('category', models.CharField(choices=[('overalls', 'Overalls'), ('tops', 'Tops'), ('bottoms', 'Bottoms'), ('outwear', 'Outwears'), ('underwears', 'Underwears')], max_length=50)),
                ('size', models.CharField(choices=[('newborns', '0-1'), ('babies', '1-5'), ('kids', '5-10'), ('xs', 'XS'), ('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL'), ('xxl', 'XXL'), ('xxxl', 'XXXL')], max_length=50)),
            ],
            bases=('user.helpneed',),
        ),
    ]
