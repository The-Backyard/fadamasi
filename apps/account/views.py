from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    RegisterSerializer,
    TokenObtainPairSerializerWithUser,
)


class TokenObtainPairViewWithUser(TokenObtainPairView):
    """Custom view to obtain JWT token pair with user information."""

    serializer_class = TokenObtainPairSerializerWithUser


class RegisterView(generics.CreateAPIView):
    """View to handle user registration."""

    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]
