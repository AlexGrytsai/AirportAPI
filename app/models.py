from django.db import models


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
