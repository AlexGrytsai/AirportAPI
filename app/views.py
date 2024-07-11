from typing import List

from django.db.models import QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from app.models import AirplaneType, Airplane, Crew
from app.serializers import AirplaneTypeSerializer, AirplaneSerializer, \
    AirplaneListSerializer, AirplaneDetailSerializer, CrewSerializer, \
    CrewListSerializer, CrewDetailSerializer


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


class CrewViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on crew members.
    """
    queryset = Crew.objects.all()

    def get_permissions(self):
        """
        Returns the appropriate permissions based on the request method.
        """
        if self.request.method in ("PUT", "PATCH", "DELETE", "POST"):
            return (IsAdminUser(),)
        if self.request.method == "GET":
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action.
        """
        if self.action == "list":
            return CrewListSerializer
        if self.action == "retrieve":
            return CrewDetailSerializer
        return CrewSerializer

    @staticmethod
    def _params_to_ints(qs: str) -> List[int]:
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self) -> QuerySet:
        """
        Returns the appropriate queryset based on the query parameters.
        """
        title = self.request.query_params.get("title")
        crew_id = self.request.query_params.get("crew_id")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        queryset = super(CrewViewSet, self).get_queryset()

        if title:
            queryset = queryset.filter(title__icontains=title)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        if crew_id:
            crew_ids = self._params_to_ints(crew_id)
            queryset = queryset.filter(id__in=crew_ids)

        return queryset
