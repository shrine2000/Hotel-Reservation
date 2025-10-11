from django.db import models
from django.contrib.auth.models import User

from reservations.models.base_models import UIDModel, TimestampedModel


class Hotel(UIDModel, TimestampedModel):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotels")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def restore(self):
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
