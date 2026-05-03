from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework.request import Request

from reservations.enums import ReservationStatus
from reservations.models.base_models import TimestampedModel, UUIDModel


class Reservation(UUIDModel, TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations"
    )
    room = models.ForeignKey(
        "Room", on_delete=models.CASCADE, related_name="reservations"
    )
    check_in_date = models.DateField(db_index=True)
    number_of_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(365)]
    )
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    status = models.CharField(
        max_length=2,
        choices=ReservationStatus.choices(),
        default=ReservationStatus.PENDING.value,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"Reservation {self.uid} by {self.user.username}"

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.user_id == request.user.pk

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.user_id == request.user.pk

    def soft_delete(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active"])
