import os
from typing import Any

import requests
from rest_framework import serializers

from app.models import AirplaneType, Airplane, Crew, Airport, Route


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
        fields = (
            "id", "name", "airplane_type", "total_seats"
        )


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
            "id",
            "name",
            "country",
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
            "id",
            "source",
            "destination",
            "distance",
        )
