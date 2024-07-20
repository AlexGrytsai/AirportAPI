from typing import List

from django.db.models import QuerySet, F, Count
from drf_spectacular.utils import extend_schema_view, extend_schema, \
    OpenApiParameter
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


@extend_schema_view(
    list=extend_schema(
        tags=["Airplanes"],
        parameters=[
            OpenApiParameter(
                name="type",
                description="Filter airplanes by type "
                            "(case-insensitive substring match)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="total_seats",
                description="Filter airplanes with a total number of seats "
                            "less than or equal to the specified value",
                required=False,
                type=int,
            ),
        ],
        description="Retrieve a list of airplanes, with optional filtering by "
                    "type and total number of seats.",
    ),
    retrieve=extend_schema(
        tags=["Airplanes"],
        description="Retrieve a single airplane by ID."
    ),
    create=extend_schema(
        tags=["Airplanes"],
        description="Create a new airplane. Requires admin privileges."
    ),
    update=extend_schema(
        tags=["Airplanes"],
        description="Update an existing airplane. Requires admin privileges."
    ),
    partial_update=extend_schema(
        tags=["Airplanes"],
        description="Partially update an existing airplane. "
                    "Requires admin privileges."
    ),
    destroy=extend_schema(
        tags=["Airplanes"],
        description="Delete an existing airplane. Requires admin privileges."
    ),
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
            queryset = queryset.filter(
                airplane_type__name__icontains=airplane_type)

        if total_seats:
            total_seats = int(total_seats)
            queryset = queryset.annotate(
                total_seats_in_plane=F("rows") * F("seats_in_row")
            ).filter(total_seats_in_plane__lte=total_seats)

        return queryset


@extend_schema_view(
    list=extend_schema(
        tags=["Crew"],
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter crew members by title "
                            "(case-insensitive substring match)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="first_name",
                description="Filter crew members by first name "
                            "(case-insensitive substring match)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter crew members by last name "
                            "(case-insensitive substring match)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="crew_id",
                description="Filter crew members by IDs "
                            "(comma-separated list of IDs)",
                required=False,
                type=str,
            ),
        ],
        description="Retrieve a list of crew members, with optional filtering "
                    "by title, first name, last name, and crew ID.",
    ),
    retrieve=extend_schema(
        tags=["Crew"],
        description="Retrieve a single crew member by ID."
    ),
    create=extend_schema(
        tags=["Crew"],
        description="Create a new crew member. Requires admin privileges."
    ),
    update=extend_schema(
        tags=["Crew"],
        description="Update an existing crew member. "
                    "Requires admin privileges."
    ),
    partial_update=extend_schema(
        tags=["Crew"],
        description="Partially update an existing crew member. "
                    "Requires admin privileges."
    ),
    destroy=extend_schema(
        tags=["Crew"],
        description="Delete an existing crew member. "
                    "Requires admin privileges."
    ),
)
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


@extend_schema_view(
    list=extend_schema(
        tags=["Airports"],
        parameters=[
            OpenApiParameter(
                name="city",
                description="Filter airports by city "
                            "(case-insensitive substring match)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="country",
                description="Filter airports by country "
                            "(case-insensitive substring match)",
                required=False,
                type=str,
            ),
        ],
        description="Retrieve a list of airports, with optional filtering "
                    "by city and country.",
    ),
    retrieve=extend_schema(
        tags=["Airports"],
        description="Retrieve a single airport by ID."
    ),
    create=extend_schema(
        tags=["Airports"],
        description="Create a new airport. Requires admin privileges."
    ),
    update=extend_schema(
        tags=["Airports"],
        description="Update an existing airport. Requires admin privileges."
    ),
    partial_update=extend_schema(
        tags=["Airports"],
        description="Partially update an existing airport. "
                    "Requires admin privileges."
    ),
    destroy=extend_schema(
        tags=["Airports"],
        description="Delete an existing airport. Requires admin privileges."
    ),
)
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


@extend_schema_view(
    list=extend_schema(
        tags=["Flights"],
        parameters=[
            OpenApiParameter(
                name="available_seats",
                description="Filter flights by available seats",
                required=False,
                type=int,
            ),
        ],
        description="Retrieve a list of flights, with optional "
                    "filtering by available seats.",
    ),
    retrieve=extend_schema(
        tags=["Flights"],
        description="Retrieve a single flight by ID."
    ),
    create=extend_schema(
        tags=["Flights"],
        description="Create a new flight. Requires admin privileges."
    ),
    update=extend_schema(
        tags=["Flights"],
        description="Update an existing flight. Requires admin privileges."
    ),
    partial_update=extend_schema(
        tags=["Flights"],
        description="Partially update an existing flight. "
                    "Requires admin privileges."
    ),
    destroy=extend_schema(
        tags=["Flights"],
        description="Delete an existing flight. Requires admin privileges."
    ),
)
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
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
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


@extend_schema_view(
    list=extend_schema(
        tags=["Orders"],
        description="Retrieve a list of orders. Requires authentication.",
    ),
    retrieve=extend_schema(
        tags=["Orders"],
        description="Retrieve a single order by ID. Requires authentication.",
    ),
    create=extend_schema(
        tags=["Orders"],
        description="Create a new order. Requires authentication.",
    ),
    update=extend_schema(
        tags=["Orders"],
        description="Update an existing order. Requires admin privileges.",
    ),
    partial_update=extend_schema(
        tags=["Orders"],
        description="Partially update an existing order. "
                    "Requires admin privileges.",
    ),
    destroy=extend_schema(
        tags=["Orders"],
        description="Delete an existing order. Requires admin privileges.",
    ),
)
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
