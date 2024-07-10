from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser
)

from user.models import User
from user.permissions import IsNotAuthenticatedOrAdmin
from user.serializers import UserSerializer


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
