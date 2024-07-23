import pycountry
from django.conf import settings
from django.db import models
from django.utils import timezone
from geopy.distance import distance
from rest_framework.exceptions import ValidationError

from user.models import User


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
        max_length=8, unique=True, help_text="Airplane code (like 'AB123')"
    )
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    @property
    def total_seats(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} " f"(total seats: {self.total_seats})"


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
        max_length=3, unique=True, help_text="Airport code (like 'JFK')"
    )
    name = models.CharField(max_length=64, help_text="Airport name")
    city = models.CharField(max_length=64, null=True, blank=True)
    state = models.CharField(max_length=64, null=True, blank=True)
    country = models.CharField(max_length=64)
    lat = models.FloatField(
        null=True,
        blank=True,
        help_text="Longitude in degrees (format: 30.752)"
    )
    lon = models.FloatField(
        null=True,
        blank=True,
        help_text="Latitude in degrees (format: 30.752)"
    )

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


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="source"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination"
    )

    def __str__(self):
        return f"{self.source.name} " \
               f"-> {self.destination.name} ({self.distance} km)"

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination cannot be the same")

    @property
    def distance(self):
        source_coordinates = (self.source.lat, self.source.lon)
        destination_coordinates = (self.destination.lat, self.destination.lon)
        calculated_destination = int(
            distance(source_coordinates, destination_coordinates).km
        )

        return calculated_destination


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    crew = models.ManyToManyField(Crew, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return (
            f"{self.route.source.name} -> {self.route.destination.name} "
            f"({self.airplane.code}, {self.departure_time})"
        )

    def clean(self):
        if self.departure_time < timezone.now():
            raise ValidationError("Departure time cannot be in the past")

        if self.arrival_time < self.departure_time:
            raise ValidationError(
                "Arrival time cannot be before departure time"
            )

        if self.arrival_time < timezone.now():
            raise ValidationError("Arrival time cannot be in the past")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user} ({self.created_at})"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    row = models.IntegerField()
    seat = models.IntegerField()

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row, self.seat, self.flight.airplane, ValidationError
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]

    def __str__(self):
        return f"Ticket #{self.id} (row: {self.row}, seat: {self.seat})"
