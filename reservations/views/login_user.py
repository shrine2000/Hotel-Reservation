from typing import Any

from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from reservations.serializers import LoginSerializer


class LoginThrottle(UserRateThrottle):
    rate = "5/minute"


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
