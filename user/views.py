from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from user.models import User
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """
    API view for creating a new user.
    """
    serializer_class = UserSerializer
    queryset = User.objects.none()


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
