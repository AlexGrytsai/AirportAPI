# Generated by Django 5.0.6 on 2024-07-11 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_alter_airplane_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Crew",
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
                ("first_name", models.CharField(max_length=64)),
                ("last_name", models.CharField(max_length=64)),
                (
                    "title",
                    models.CharField(
                        choices=[
                            ("Captain", "Captain"),
                            ("Co-Pilot", "Co-Pilot"),
                            ("Flight Attendant", "Flight Attendant"),
                            ("Flight Engineer", "Flight Engineer"),
                            ("Flight Medic", "Flight Medic"),
                        ],
                        max_length=64,
                    ),
                ),
            ],
        ),
    ]
