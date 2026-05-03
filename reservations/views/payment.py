import logging
from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets, status, filters
from rest_framework.request import Request
from rest_framework.response import Response

from reservations.filters import PaymentFilter
from reservations.models.payment import Payment
from reservations.serializers.payment_serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
)
from reservations.services import payment_svc

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    lookup_field = "uid"
    http_method_names = ["get", "post", "head", "options"]
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filterset_class = PaymentFilter
    ordering_fields = ["amount", "created_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            Payment.objects.select_related("reservation__user")
            .only(
                "uid",
                "amount",
                "payment_method",
                "status",
                "reference_id",
                "notes",
                "created_at",
                "reservation__uid",
                "reservation__user_id",
            )
            .order_by("-created_at")
        )
        if not self.request.user.is_staff:
            qs = qs.filter(reservation__user=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentCreateSerializer
        return PaymentSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation = serializer.validated_data["reservation_uid"]

        if not request.user.is_staff and reservation.user_id != request.user.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)

        payment = payment_svc.create_payment(
            reservation=reservation,
            amount=serializer.validated_data["amount"],
            payment_method=serializer.validated_data["payment_method"],
            reference_id=serializer.validated_data.get("reference_id", ""),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
