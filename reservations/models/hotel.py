from django.db import models
from django.contrib.auth.models import User

from reservations.models.base_models import UIDModel, TimestampedModel


class Hotel(UIDModel, TimestampedModel):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
