from django.db import models


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Airplane(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
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
