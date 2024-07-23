from typing import List

from django.db.models import (
    QuerySet,
    F,
    Count
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    PolymorphicProxySerializer
)
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from app.models import (
    Airplane,
    Crew,
    Airport,
    Flight,
    Order
)
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
    OrderListSerializer,
    OrderDetailSerializer,
    OrderListForStaffSerializer,
    OrderDetailForStaffSerializer,
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
        responses={
            200: AirplaneListSerializer,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT
        },
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
        description="Retrieve a list of orders.",
        tags=["Orders"],
        responses={
            200: PolymorphicProxySerializer(
                component_name="OrderDetail",
                serializers={
                    "staff": OrderListForStaffSerializer,
                    "default": OrderListSerializer
                },
                resource_type_field_name="role",
            ),
        },
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID (staff only)",
                required=False,
                type=int
            ),
            OpenApiParameter(
                name="order_id",
                description="Filter by order ID",
                required=False,
                type=int
            ),
            OpenApiParameter(
                name="flight_id",
                description="Filter by flight ID",
                required=False,
                type=int
            ),
        ],
        examples=[
            OpenApiExample(
                name="For Staff",
                description="Retrieve a list of orders for staff.",
                value=[
                    {
                        "id": 4,
                        "created_at": "2024-07-23T11:37:34.334234+03:00",
                        "tickets": [
                            {
                                "flight": "Anaa Airport(French Polynesia) "
                                          "-> El Mellah Airport(Algeria)",
                                "row": 2,
                                "seat": 2
                            }
                        ],
                        "user": {
                            "id": 1,
                            "email": "test@test.com"
                        }
                    },
                ],
                response_only=True
            ),
            OpenApiExample(
                name="For Customers",
                description="Retrieve a list of orders for customers.",
                value=[
                    {
                        "id": 4,
                        "created_at": "2024-07-23T11:37:34.334234+03:00",
                        "tickets": [
                            {
                                "flight": "Anaa Airport(French Polynesia) "
                                          "-> El Mellah Airport(Algeria)",
                                "row": 2,
                                "seat": 2
                            }
                        ],
                    }
                ]
            )
        ]
    ),
    retrieve=extend_schema(
        description="Retrieve an order by its ID.",
        tags=["Orders"],
        responses={
            200: PolymorphicProxySerializer(
                component_name="OrderDetail",
                serializers={
                    "staff": OrderDetailForStaffSerializer,
                    "default": OrderDetailSerializer
                },
                resource_type_field_name="role",
            ),
        },
    ),
    create=extend_schema(
        description="Create a new order.",
        tags=["Orders"],
    ),
    update=extend_schema(
        description="Update an order.",
        tags=["Orders"],
    ),
    partial_update=extend_schema(
        description="Partially update an order.",
        tags=["Orders"],
    ),
    destroy=extend_schema(
        description="Delete an order.",
        tags=["Orders"],
    )
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on orders.
    """

    serializer_class = OrderSerializer
    queryset = Order.objects.all().prefetch_related(
        "tickets__flight__route__source",
        "tickets__flight__route__destination"
    )

    def get_permissions(self):
        """
        Returns the appropriate permissions based on the request method.
        """
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return (IsAdminUser(),)
        return (IsAuthenticated(),)

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action.
        """
        user = self.request.user
        if self.action == "list" and user.is_staff:
            return OrderListForStaffSerializer
        if self.action == "retrieve" and user.is_staff:
            return OrderDetailForStaffSerializer
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Returns the appropriate queryset based on the query parameters.
        """
        queryset = super(OrderViewSet, self).get_queryset()
        user = self.request.user

        user_id = self.request.query_params.get("user_id")
        order_id = self.request.query_params.get("order_id")
        flight_id = self.request.query_params.get("flight_id")

        if not user.is_staff:
            queryset = super(OrderViewSet, self).get_queryset().filter(
                user=user
            )
        if user.is_staff:
            queryset = queryset.select_related("user")
        if order_id:
            queryset = queryset.filter(id=order_id)
        if flight_id:
            queryset = queryset.filter(tickets__flight__id=flight_id)
        if user_id and user.is_staff:
            queryset = queryset.filter(user__id=user_id).select_related("user")

        return queryset
