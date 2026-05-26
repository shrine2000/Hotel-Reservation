import logging
from typing import Any

from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets, status, filters
from rest_framework.request import Request
from rest_framework.response import Response

from reservations.models.guest import GuestProfile
from reservations.serializers.guest_serializers import (
    GuestProfileCreateSerializer,
    GuestProfileSerializer,
    GuestProfileUpdateSerializer,
)
from reservations.services import guest_svc

logger = logging.getLogger(__name__)


class GuestProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    lookup_field = "uid"
    http_method_names = ["get", "post", "patch", "head", "options"]
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            GuestProfile.objects.using("replica")
            .select_related("user")
            .only(
                "uid",
                "phone",
                "address",
                "id_type",
                "id_number",
                "created_at",
                "user__username",
                "user__email",
                "user_id",
            )
            .order_by("-created_at")
        )
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return GuestProfileCreateSerializer
        if self.action in ("update", "partial_update"):
            return GuestProfileUpdateSerializer
        return GuestProfileSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = GuestProfileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = guest_svc.create_guest_profile(
            user=request.user, **serializer.validated_data
        )
        return Response(
            GuestProfileSerializer(profile).data, status=status.HTTP_201_CREATED
        )

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        profile = self.get_object()
        serializer = GuestProfileUpdateSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        updated = guest_svc.update_guest_profile(profile, **serializer.validated_data)
        return Response(GuestProfileSerializer(updated).data)
