# Generated by Django 5.0.6 on 2024-07-12 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_airport_lat_airport_lon_route"),
    ]

    operations = [
        migrations.AlterField(
            model_name="route",
            name="distance",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
