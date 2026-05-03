from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework.request import Request

from reservations.models.base_models import CustomIDModel, TimestampedModel
from reservations.validators import CharacterPatternValidator


class HotelReview(CustomIDModel, TimestampedModel):
    id_prefix = "HR"

    hotel = models.ForeignKey("Hotel", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(
        blank=True, validators=[CharacterPatternValidator("SAFE_TEXT")]
    )

    class Meta:
        unique_together = [("hotel", "user")]

    def __str__(self) -> str:
        return f"Review by {self.user_id} on {self.hotel_id} ({self.rating}★)"

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.user_id == request.user.pk
