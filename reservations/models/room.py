from django.db import models
from rest_framework.request import Request

from reservations.models import Hotel
from reservations.models.base_models import UIDModel, TimestampedModel
from reservations.enums import RoomType, RoomLuxury


class Room(UIDModel, TimestampedModel):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=1, choices=RoomType.choices())
    luxury = models.CharField(max_length=2, choices=RoomLuxury.choices())
    base_cost = models.DecimalField(max_digits=8, decimal_places=2)
    available_rooms = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.hotel.name} - {self.room_type} - {self.luxury}"

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated and request.user.is_staff

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.hotel.admin == request.user

    def soft_delete(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def restore(self) -> None:
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
