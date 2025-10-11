from django.db import models

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

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type} - {self.luxury}"

    @staticmethod
    def has_read_permission(request):
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request):
        return request.user.is_authenticated and request.user.is_staff

    def has_object_read_permission(self, request):
        return request.user.is_authenticated

    def has_object_write_permission(self, request):
        return request.user.is_staff or self.hotel.admin == request.user
