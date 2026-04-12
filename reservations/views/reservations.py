from typing import Any

from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions

from reservations.models import Reservation
from reservations.serializers import ReservationSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("user", "room").filter(is_active=True)
    serializer_class = ReservationSerializer
    permission_classes = (DRYPermissions,)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
