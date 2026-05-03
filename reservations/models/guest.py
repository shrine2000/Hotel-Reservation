from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.request import Request

from reservations.models.base_models import CustomIDModel, TimestampedModel
from reservations.validators import CharacterPatternValidator


class GuestProfile(CustomIDModel, TimestampedModel):
    id_prefix = "GP"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guest_profile"
    )
    phone = PhoneNumberField(blank=True)
    address = models.TextField(
        blank=True, validators=[CharacterPatternValidator("ADDRESS")]
    )
    id_type = models.CharField(
        max_length=30,
        blank=True,
        validators=[CharacterPatternValidator("ALPHANUMERIC")],
    )
    id_number = models.CharField(
        max_length=50,
        blank=True,
        validators=[CharacterPatternValidator("ALPHANUMERIC_WITH_DASH")],
    )

    def __str__(self) -> str:
        return f"GuestProfile({self.user.username})"

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.user_id == request.user.pk

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.user_id == request.user.pk
