from django.db import models
from django.contrib.auth.models import User

from reservations.models.base_models import UIDModel, TimestampedModel


class Reservation(UIDModel, TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    check_in_date = models.DateField()
    number_of_days = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.room.base_cost * self.number_of_days
        if self.room.available_rooms < 1:
            raise ValueError("No rooms available")
        self.room.available_rooms -= 1
        self.room.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.id} by {self.user.username}"
