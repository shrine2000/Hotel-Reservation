import logging
from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets, filters, status
from rest_framework.request import Request
from rest_framework.response import Response

from reservations.filters import RoomFilter
from reservations.models.room import Room
from reservations.serializers.room_serializers import (
    RoomCreateSerializer,
    RoomSerializer,
    RoomUpdateSerializer,
)

logger = logging.getLogger(__name__)


class RoomViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    lookup_field = "uid"
    http_method_names = ["get", "post", "patch", "head", "options"]
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    search_fields = ["hotel__name", "hotel__location"]
    filterset_class = RoomFilter
    ordering_fields = ["base_cost", "available_rooms", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Room.objects.select_related("hotel")
            .only(
                "uid",
                "room_type",
                "luxury",
                "base_cost",
                "available_rooms",
                "is_active",
                "created_at",
                "hotel__uid",
                "hotel__name",
            )
            .filter(is_active=True)
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return RoomCreateSerializer
        if self.action in ("update", "partial_update"):
            return RoomUpdateSerializer
        return RoomSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = RoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
