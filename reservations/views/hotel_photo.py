import logging
from typing import Any

from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets, status, filters
from rest_framework.request import Request
from rest_framework.response import Response

from reservations.models.hotel_photo import HotelPhoto
from reservations.serializers.hotel_photo_serializers import (
    HotelPhotoCreateSerializer,
    HotelPhotoSerializer,
)

logger = logging.getLogger(__name__)


class HotelPhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    lookup_field = "uid"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filter_backends = (filters.OrderingFilter,)
    ordering = ["-is_primary", "created_at"]

    def get_queryset(self):
        qs = (
            HotelPhoto.objects.select_related("hotel")
            .only(
                "uid",
                "url",
                "caption",
                "is_primary",
                "created_at",
                "hotel__uid",
                "hotel_id",
                "hotel__admin_id",
            )
            .order_by("-is_primary", "created_at")
        )
        hotel_uid = self.request.query_params.get("hotel")
        if hotel_uid:
            qs = qs.filter(hotel__uid=hotel_uid)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return HotelPhotoCreateSerializer
        return HotelPhotoSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = HotelPhotoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        hotel = serializer.validated_data["hotel_uid"]

        if not request.user.is_staff and hotel.admin_id != request.user.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if serializer.validated_data.get("is_primary"):
            HotelPhoto.objects.filter(hotel=hotel, is_primary=True).update(
                is_primary=False
            )

        photo = HotelPhoto.objects.create(
            hotel=hotel,
            url=serializer.validated_data["url"],
            caption=serializer.validated_data.get("caption", ""),
            is_primary=serializer.validated_data.get("is_primary", False),
        )
        return Response(
            HotelPhotoSerializer(photo).data, status=status.HTTP_201_CREATED
        )
