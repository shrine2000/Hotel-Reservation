from typing import Any

from django.db import models, transaction
from django.contrib.auth.models import User
from rest_framework.request import Request

from reservations.models.base_models import UIDModel, TimestampedModel
from reservations.exceptions import NoRoomsAvailableError


class Reservation(UIDModel, TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    check_in_date = models.DateField()
    number_of_days = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk is None:
            with transaction.atomic():
                # Re-fetch with a row-level lock so concurrent bookings serialize here.
                # select_for_update() is a no-op on SQLite; migrate to PostgreSQL for real protection.
                from reservations.models.room import Room

                room = Room.objects.select_for_update().get(pk=self.room_id)
                if room.available_rooms < 1:
                    raise NoRoomsAvailableError()
                room.available_rooms -= 1
                room.save(update_fields=["available_rooms"])
                self.total_cost = room.base_cost * self.number_of_days
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Reservation {self.id} by {self.user.username}"

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.user == request.user

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.user == request.user

    def soft_delete(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])
