from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.request import Request

from reservations.enums import PaymentMethod, PaymentStatus
from reservations.models.base_models import CustomIDModel, TimestampedModel
from reservations.validators import CharacterPatternValidator


class Payment(CustomIDModel, TimestampedModel):
    id_prefix = "PAY"

    reservation = models.ForeignKey(
        "Reservation", on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    payment_method = models.CharField(max_length=2, choices=PaymentMethod.choices())
    status = models.CharField(
        max_length=2,
        choices=PaymentStatus.choices(),
        default=PaymentStatus.PENDING.value,
        db_index=True,
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        validators=[CharacterPatternValidator("REFERENCE_ID")],
    )
    notes = models.TextField(
        blank=True, validators=[CharacterPatternValidator("SAFE_TEXT")]
    )

    class Meta:
        indexes = [
            models.Index(fields=["reservation", "status"]),
        ]

    def __str__(self) -> str:
        return f"Payment {self.uid} [{self.status}]"

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.reservation.user_id == request.user.pk

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.reservation.user_id == request.user.pk
