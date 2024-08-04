from django.db import models
from django.contrib.auth.models import User

from reservations.models.base_models import UIDModel, TimestampedModel
from reservations.models.enums import RoomType, RoomLuxury


class Hotel(UIDModel, TimestampedModel):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    admin = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Room(UIDModel, TimestampedModel):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=1, choices=RoomType.choices())
    luxury = models.CharField(max_length=2, choices=RoomLuxury.choices())
    base_cost = models.DecimalField(max_digits=8, decimal_places=2)
    available_rooms = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type} - {self.luxury}"


class Reservation(UIDModel, TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    number_of_days = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_cost = self.room.base_cost * self.number_of_days
        if self.room.available_rooms < 1:
            raise ValueError("No rooms available")
        self.room.available_rooms -= 1
        self.room.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.id} by {self.user.username}"
