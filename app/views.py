from rest_framework import generics, mixins, viewsets

from app.models import AirplaneType, Airplane
from app.serializers import AirplaneTypeSerializer, AirplaneSerializer, \
    AirplaneListSerializer


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer
