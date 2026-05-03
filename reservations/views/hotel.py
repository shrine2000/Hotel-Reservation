import logging

from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from reservations.filters import HotelFilter
from reservations.models.hotel import Hotel
from reservations.serializers.hotel_serializers import (
    HotelCreateSerializer,
    HotelDetailSerializer,
    HotelSerializer,
    HotelUpdateSerializer,
)

logger = logging.getLogger(__name__)


class HotelViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    lookup_field = "uid"
    http_method_names = ["get", "post", "patch", "head", "options"]
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    search_fields = ["name", "location"]
    filterset_class = HotelFilter
    ordering_fields = ["name", "star_rating", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Hotel.objects.select_related("admin")
            .prefetch_related("photos", "reviews")
            .annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
            .filter(is_active=True)
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return HotelCreateSerializer
        if self.action in ("update", "partial_update"):
            return HotelUpdateSerializer
        if self.action == "retrieve":
            return HotelDetailSerializer
        return HotelSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = HotelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hotel = serializer.save(admin=request.user)
        return Response(HotelSerializer(hotel).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="deactivate")
    def deactivate(self, request: Request, uid: str | None = None) -> Response:
        hotel = self.get_object()
        hotel.soft_delete()
        return Response(status=status.HTTP_200_OK)
