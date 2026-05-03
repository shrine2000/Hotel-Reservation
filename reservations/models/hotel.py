from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from rest_framework.request import Request

from reservations.models.base_models import TimestampedModel, UUIDModel
from reservations.validators import CharacterPatternValidator


class Hotel(UUIDModel, TimestampedModel):
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2), CharacterPatternValidator("COMPANY_NAME")],
    )
    location = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2), CharacterPatternValidator("ADDRESS")],
    )
    description = models.TextField(
        validators=[CharacterPatternValidator("SAFE_TEXT")],
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hotels"
    )
    star_rating = models.PositiveSmallIntegerField(
        default=3,
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated and request.user.is_staff

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.admin_id == request.user.pk

    def soft_delete(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active"])

    def restore(self) -> None:
        self.is_active = True
        self.save(update_fields=["is_active"])
