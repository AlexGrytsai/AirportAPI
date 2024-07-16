import os
from typing import Any

import requests
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.models import AirplaneType, Airplane, Crew, Airport, Route, Flight, \
    Ticket


class AirplaneTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the AirplaneType model.
    """

    class Meta:
        model = AirplaneType
        fields = ("id", "name",)


class AirplaneSerializer(serializers.ModelSerializer):
    """
    Default serializer for the Airplane model.
    """

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "code",
            "rows",
            "seats_in_row",
            "airplane_type",
            "total_seats"
        )


class AirplaneListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing airplanes.
    """
    airplane_type = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )

    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type")


class AirplaneDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed airplane information.
    """
    airplane_type = AirplaneTypeSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "code",
            "rows",
            "seats_in_row",
            "airplane_type",
            "total_seats"
        )


class CrewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Crew model.
    """

    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "title",
        )


class CrewListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing crew members.
    """

    class Meta:
        model = Crew
        fields = (
            "id",
            "full_name",
            "title",
        )


class CrewDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed crew member information.
    """

    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "title",
        )


class AirportSerializer(serializers.ModelSerializer):
    """
    Serializer for the Airport model.
    """

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "code",
            "state",
            "city",
            "country",
            "lat",
            "lon",
        )


class AirportListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing airports.
    """

    class Meta:
        model = Airport
        fields = (
            "name",
            "country",
            "city",
        )


class AirportDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed airport information.
    """

    @staticmethod
    def actual_weather(city: str) -> dict[str, str | Any]:
        url = (f"https://api.weatherapi.com/v1/current.json"
               f"?key={os.getenv('WEATHER_KEY')}&q={city}")
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(
                f"Error {response.status_code}: {response.text}")
        else:
            response = response.json()
            weather_data = {
                "localtime": response["location"]["localtime"],
                "temperature": f"{response['current']['temp_c']} Celsius "
                               f"(feels like "
                               f"{response['current']['feelslike_c']} "
                               f"Celsius)",
                "condition": response["current"]["condition"]["text"]
            }
            return weather_data

    weather = serializers.SerializerMethodField()

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "code",
            "state",
            "city",
            "country",
            "weather",
        )

    def get_weather(self, obj):
        return self.actual_weather(obj.city)


class RouteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Route model.
    """

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
        )


class RouteListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing routes.
    """
    source = AirportListSerializer(read_only=True)
    destination = AirportListSerializer(read_only=True)

    class Meta:
        model = Route
        fields = (
            "source",
            "destination",
            "distance",
        )


class FlightSerializer(serializers.ModelSerializer):
    """
    Serializer for the Flight model.
    """
    route = RouteSerializer(read_only=False)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
        )

    def create(self, validated_data):
        route_data = validated_data.pop("route")
        crew_data = validated_data.pop("crew")
        route = Route.objects.create(**route_data)

        flight = Flight.objects.create(route=route, **validated_data)
        flight.crew.set(crew_data)

        return flight

    def update(self, instance, validated_data):
        route_data = validated_data.pop("route")
        crew_data = validated_data.pop("crew")

        instance.airplane = validated_data.get("airplane", instance.airplane)
        instance.departure_time = validated_data.get(
            "departure_time", instance.departure_time
        )
        instance.arrival_time = validated_data.get(
            "arrival_time", instance.arrival_time
        )
        instance.save()

        if crew_data is not None:
            instance.crew.set(crew_data)

        route = instance.route
        route.source = route_data.get("source", route.source)
        route.destination = route_data.get("destination", route.destination)
        route.save()

        return instance


class FlightListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing flights.
    """
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "available_seats",
            "departure_time",
            "arrival_time",
        )


class TicketSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for the Ticket model.
    """

    def validate(self, attrs: dict) -> dict:
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = (
            "flight",
            "row",
            "seat",
        )


class FlightDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed flight information.
    """
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewListSerializer(many=True, read_only=True)
    taken_seats = TicketSeatSerializer(
        many=True, read_only=True, source="tickets"
    )
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "available_seats",
            "taken_seats",
            "crew",
            "departure_time",
            "arrival_time",
        )
