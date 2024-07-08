from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """
    API view for creating a new user.
    """
    serializer_class = UserSerializer
