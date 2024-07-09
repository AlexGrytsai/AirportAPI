from rest_framework import serializers

from app.models import AirplaneType, Airplane


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name",)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "name", "code", "rows", "seats_in_row", "airplane_type",
            "total_seats")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id", "name", "airplane_type",
            "total_seats")
