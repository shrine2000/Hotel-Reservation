from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny

from reservations.serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
