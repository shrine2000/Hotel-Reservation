from django.db import models
from rest_framework.request import Request

from reservations.models.base_models import CustomIDModel, TimestampedModel
from reservations.validators import CharacterPatternValidator, validate_not_blank


class HotelPhoto(CustomIDModel, TimestampedModel):
    id_prefix = "HP"

    hotel = models.ForeignKey("Hotel", on_delete=models.CASCADE, related_name="photos")
    url = models.URLField(max_length=500)
    caption = models.CharField(
        max_length=200,
        blank=True,
        validators=[validate_not_blank, CharacterPatternValidator("SAFE_TEXT")],
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "created_at"]

    def __str__(self) -> str:
        return f"Photo for {self.hotel_id} ({'primary' if self.is_primary else 'secondary'})"

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated and request.user.is_staff

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.hotel.admin_id == request.user.pk
