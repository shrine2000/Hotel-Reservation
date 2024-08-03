from django.db import models
from django.contrib.auth.models import User


class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    admin = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Room(models.Model):
    SINGLE = "S"
    DOUBLE = "D"
    ROOM_TYPES = [
        (SINGLE, "Single"),
        (DOUBLE, "Double"),
    ]

    DELUXE = "D"
    SUPER_DELUXE = "SD"
    ROOM_LUXURY = [
        (DELUXE, "Deluxe"),
        (SUPER_DELUXE, "Super Deluxe"),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=1, choices=ROOM_TYPES)
    luxury = models.CharField(max_length=2, choices=ROOM_LUXURY)
    base_cost = models.DecimalField(max_digits=8, decimal_places=2)
    available_rooms = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type} - {self.luxury}"


class Reservation(models.Model):
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
