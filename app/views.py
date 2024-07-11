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
    """
    A viewset for creating and listing airplane types.
    """
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()


class AirplaneViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on airplanes.
    """
    queryset = Airplane.objects.all().select_related()

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action.
        """
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer

    def get_permissions(self):
        """
        Returns the appropriate permissions based on the request method.
        """
        if self.request.method in ("PUT", "PATCH", "DELETE", "POST"):
            return (IsAdminUser(),)
        return super().get_permissions()
