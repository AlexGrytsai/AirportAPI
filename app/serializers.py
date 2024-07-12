from rest_framework import serializers

from app.models import AirplaneType, Airplane, Crew, Airport


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
