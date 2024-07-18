from typing import List

from django.db.models import QuerySet, F, Count
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from app.models import Airplane, Crew, Airport, Flight, Order
from app.serializers import (
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    CrewSerializer,
    CrewListSerializer,
    CrewDetailSerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
)


class AirplaneViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on airplanes.
    """

    queryset = Airplane.objects.all().select_related()
    permission_classes = (IsAuthenticated,)

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

    def get_queryset(self) -> QuerySet:
        """
        Returns the appropriate queryset based on the query parameters.
        """
        airplane_type = self.request.query_params.get("type")
        total_seats = self.request.query_params.get("total_seats")

        queryset = super(AirplaneViewSet, self).get_queryset()

        if airplane_type:
            queryset = queryset.filter(airplane_type__icontains=airplane_type)

        if total_seats:
            total_seats = int(total_seats)
            queryset = queryset.annotate(
                total_seats_in_plane=F("rows") * F("seats_in_row")
            ).filter(total_seats_in_plane__lte=total_seats)

        return queryset


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


class AirportViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on airports.
    """

    queryset = Airport.objects.all()

    def get_permissions(self):
        """
        Returns the appropriate permissions based on the request method.
        """
        if self.request.method in ("PUT", "PATCH", "DELETE", "POST"):
            return (IsAdminUser(),)
        return (IsAuthenticated(),)

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action.
        """
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        return AirportSerializer

    def get_queryset(self):
        """
        Returns the appropriate queryset based on the query parameters.
        """
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")

        queryset = super(AirportViewSet, self).get_queryset()

        if city:
            queryset = queryset.filter(city__icontains=city)
        if country:
            queryset = queryset.filter(country__icontains=country)

        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on flights.
    """

    queryset = (
        Flight.objects.all()
        .select_related(
            "route__source", "route__destination", "airplane__airplane_type"
        )
        .prefetch_related("crew")
        .annotate(
            available_seats=(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )
    )

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action.
        """
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    def get_permissions(self):
        """
        Returns the appropriate permissions based on the request method.
        """
        if self.request.method in ("PUT", "PATCH", "DELETE", "POST"):
            return (IsAdminUser(),)
        return (IsAuthenticated(),)


class OrderViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on orders.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        Returns the appropriate permissions based on the request method.
        """
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return (IsAdminUser(),)
        return (IsAuthenticated(),)
