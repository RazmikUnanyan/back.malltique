"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializers,
    AuthTokenSerializers
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the  system."""
    serializer_class = UserSerializers


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializers
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializers
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve ane return user."""
        return self.request.user
