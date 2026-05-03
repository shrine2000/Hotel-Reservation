import operator
from functools import reduce

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.request import Request

from reservations.models.base_models import FullNameMixin, TimestampedModel, UUIDModel
from reservations.validators import CharacterPatternValidator


class UserManager(DjangoUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if email:
            email = self.normalize_email(email)
        user = self.model(username=username, email=email or "", **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean()
        user.save(using=self._db)
        return user

    def find_by_email_or_phone(
        self, email: str | None = None, phone: str | None = None, is_active: bool = True
    ):
        conditions: list[Q] = []
        if email:
            conditions.append(Q(email=self.normalize_email(email)))
        if phone:
            conditions.append(Q(phone=phone))
        if not conditions:
            return self.none()
        qs = self.filter(reduce(operator.or_, conditions))
        return qs.filter(is_active=True) if is_active else qs


class User(FullNameMixin, AbstractUser, UUIDModel, TimestampedModel):
    first_name = models.CharField(
        max_length=150,
        blank=True,
        validators=[CharacterPatternValidator("PERSON_NAME")],
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        validators=[CharacterPatternValidator("PERSON_NAME")],
    )
    phone = PhoneNumberField(blank=True)

    objects = UserManager()

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.username

    @staticmethod
    def has_read_permission(request: Request) -> bool:
        return request.user.is_authenticated

    @staticmethod
    def has_write_permission(request: Request) -> bool:
        return request.user.is_authenticated

    def has_object_read_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.pk == request.user.pk

    def has_object_write_permission(self, request: Request) -> bool:
        return request.user.is_staff or self.pk == request.user.pk
