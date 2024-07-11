from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser

from app.models import AirplaneType, Airplane
from app.serializers import AirplaneTypeSerializer, AirplaneSerializer, \
    AirplaneListSerializer, AirplaneDetailSerializer


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
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE", "POST"):
            return (IsAdminUser(),)
        return super().get_permissions()
