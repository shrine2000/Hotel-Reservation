from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth import get_user_model

from reservations.serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
