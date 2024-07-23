from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view
)
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
    ),
    post=extend_schema(
        summary="Create User",
        description="Create a new user "
                    "(only for staff users ur unauthenticated user).",
        tags=["User"],
        request=UserSerializer,
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
    ),
    put=extend_schema(
        summary="Update User Information",
        description="Update the authenticated user's information.",
        tags=["User"],
        request=UserSerializer,
    ),
    patch=extend_schema(
        summary="Partially Update User Information",
        description="Partially update the authenticated user's information.",
        tags=["User"],
        request=UserSerializer,
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
