import pycountry
from django.db import models
from rest_framework.exceptions import ValidationError


class AirplaneType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Airplane(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        help_text="Airplane name (like 'Boeing 747')"
    )
    code = models.CharField(
        max_length=8,
        unique=True,
        help_text="Airplane code (like 'AB123')"
    )
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    @property
    def total_seats(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return (f"Airplane {self.name}|{self.code} "
                f"(total seats: {self.total_seats})")


class TitleCrew(models.TextChoices):
    CAPTAIN = "Captain", "Captain"
    CO_PILOT = "Co-Pilot", "Co-Pilot"
    FLIGHT_ATTENDANT = "Flight Attendant", "Flight Attendant"
    FLIGHT_ENGINEER = "Flight Engineer", "Flight Engineer"
    FLIGHT_MEDIC = "Flight Medic", "Flight Medic"


class Crew(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    title = models.CharField(choices=TitleCrew.choices, max_length=64)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.title})"


class Airport(models.Model):
    code = models.CharField(
        max_length=3,
        unique=True,
        help_text="Airport code (like 'JFK')"
    )
    name = models.CharField(
        max_length=64, help_text="Airport name"
    )
    city = models.CharField(max_length=64, null=True, blank=True)
    state = models.CharField(max_length=64, null=True, blank=True)
    country = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} ({self.city} | {self.country})"

    def clean(self):
        if not self.code.isalpha():
            raise ValidationError("Code can only contain letters")
        if self.code and not self.code.isupper():
            self.code = self.code.upper()
        if not self.country:
            raise ValidationError("Country is required")

        if pycountry.countries.get(name=self.country) is None:
            raise ValidationError("Country not found")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
