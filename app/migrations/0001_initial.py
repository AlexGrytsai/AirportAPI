# Generated by Django 5.0.6 on 2024-07-09 04:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AirplaneType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Airplane",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "code",
                    models.CharField(
                        help_text="Airplane code (like 'AB123')",
                        max_length=8,
                        unique=True,
                    ),
                ),
                ("rows", models.IntegerField()),
                ("seats_in_row", models.IntegerField()),
                (
                    "airplane_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.airplanetype",
                    ),
                ),
            ],
        ),
    ]
