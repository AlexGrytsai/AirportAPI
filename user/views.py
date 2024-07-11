from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema, \
    extend_schema_view
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser
)

from user.models import User
from user.permissions import IsNotAuthenticatedOrAdmin
from user.serializers import UserSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve User List Information (only for staff users)",
        description="Retrieve User List Information (only for staff users)",
        tags=["User"],
        responses={
            200: UserSerializer,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                "Successful response",
                summary="A successful response example",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "is_staff": False
                }
            ),
            OpenApiExample(
                "Unauthorized response",
                summary="An unauthorized response example",
                value={
                    "detail": "Authentication credentials were not provided."
                }
            ),
            OpenApiExample(
                "Forbidden response",
                summary="A forbidden response example",
                value={
                    "detail":
                        "You do not have permission to perform this action."
                }
            )
        ]
    ),
    post=extend_schema(
        summary="Create User",
        description="Create a new user "
                    "(only for staff users ur unauthenticated user).",
        tags=["User"],
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Successful response",
                summary="A successful response example",
                value={
                    "id": 2,
                    "email": "new_user@example.com",
                    "is_staff": False
                }
            ),
            OpenApiExample(
                "Bad request response",
                summary="A bad request response example",
                value={
                    "email": ["This field must be unique."]
                }
            )
        ]
    )
)
class UserView(generics.ListCreateAPIView):
    """
    API view for creating a new user and listing all users (only staff).
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return (IsNotAuthenticatedOrAdmin(),)
        elif self.request.method == "GET":
            return (IsAdminUser(),)
        return super().get_permissions()


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve User Information",
        description="Retrieve the authenticated user's information.",
        tags=["User"],
        responses={
            200: UserSerializer,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Successful response",
                summary="A successful response example",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "is_staff": False
                }
            ),
            OpenApiExample(
                "Unauthorized response",
                summary="An unauthorized response example",
                value={
                    "detail": "Authentication credentials were not provided."
                }
            )
        ]
    ),
    put=extend_schema(
        summary="Update User Information",
        description="Update the authenticated user's information.",
        tags=["User"],
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Successful response",
                summary="A successful response example",
                value={
                    "id": 1,
                    "email": "updated_user@example.com",
                    "is_staff": False
                }
            ),
            OpenApiExample(
                "Bad request response",
                summary="A bad request response example",
                value={
                    "email": ["This field is required."]
                }
            ),
            OpenApiExample(
                "Unauthorized response",
                summary="An unauthorized response example",
                value={
                    "detail": "Authentication credentials were not provided."
                }
            )
        ]
    ),
    patch=extend_schema(
        summary="Partially Update User Information",
        description="Partially update the authenticated user's information.",
        tags=["User"],
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Successful response",
                summary="A successful response example",
                value={
                    "id": 1,
                    "email": "partially_updated_user@example.com",
                    "is_staff": False
                }
            ),
            OpenApiExample(
                "Bad request response",
                summary="A bad request response example",
                value={
                    "email": ["This field is required."]
                }
            ),
            OpenApiExample(
                "Unauthorized response",
                summary="An unauthorized response example",
                value={
                    "detail": "Authentication credentials were not provided."
                }
            )
        ]
    )
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    API view for managing an existing user.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Get the authenticated user.
        """
        return self.request.user
