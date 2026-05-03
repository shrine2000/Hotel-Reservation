import logging
from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from reservations.filters import ReservationFilter
from reservations.models.reservation import Reservation
from reservations.serializers.reservation_serializers import (
    ReservationCreateSerializer,
    ReservationModifySerializer,
    ReservationSerializer,
)
from reservations.services import reservation_svc

logger = logging.getLogger(__name__)


class ReservationViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    lookup_field = "uid"
    http_method_names = ["get", "post", "head", "options"]
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = ReservationFilter
    ordering_fields = ["check_in_date", "created_at", "total_cost"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            Reservation.objects.select_related("room__hotel", "user")
            .only(
                "uid",
                "check_in_date",
                "number_of_days",
                "total_cost",
                "status",
                "is_active",
                "created_at",
                "user_id",
                "room__uid",
                "room__room_type",
                "room__luxury",
                "room__hotel__name",
            )
            .order_by("-created_at")
        )
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return ReservationCreateSerializer
        if self.action == "modify":
            return ReservationModifySerializer
        return ReservationSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = reservation_svc.create_reservation(
            user=request.user,
            room=serializer.validated_data["room_uid"],
            check_in_date=serializer.validated_data["check_in_date"],
            number_of_days=serializer.validated_data["number_of_days"],
        )
        return Response(
            ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request: Request, uid: str | None = None) -> Response:
        reservation = self.get_object()
        updated = reservation_svc.confirm_reservation(reservation)
        return Response(ReservationSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="check-in")
    def check_in(self, request: Request, uid: str | None = None) -> Response:
        reservation = self.get_object()
        updated = reservation_svc.check_in_reservation(reservation)
        return Response(ReservationSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="check-out")
    def check_out(self, request: Request, uid: str | None = None) -> Response:
        reservation = self.get_object()
        updated = reservation_svc.check_out_reservation(reservation)
        return Response(ReservationSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request: Request, uid: str | None = None) -> Response:
        reservation = self.get_object()
        updated = reservation_svc.cancel_reservation(reservation)
        return Response(ReservationSerializer(updated).data)

    @action(detail=True, methods=["patch"], url_path="modify")
    def modify(self, request: Request, uid: str | None = None) -> Response:
        reservation = self.get_object()
        serializer = ReservationModifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = reservation_svc.modify_reservation(
            reservation=reservation,
            check_in_date=serializer.validated_data.get("check_in_date"),
            number_of_days=serializer.validated_data.get("number_of_days"),
        )
        return Response(ReservationSerializer(updated).data)
