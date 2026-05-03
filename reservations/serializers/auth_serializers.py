from typing import Any

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from reservations.exceptions import InvalidCredentialsError

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "email", "first_name", "last_name")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value: str) -> str:
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        return value.strip()

    def create(self, validated_data: dict[str, Any]) -> Any:
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise InvalidCredentialsError()
        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    id_type = serializers.SerializerMethodField()
    id_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "uid",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "address",
            "id_type",
            "id_number",
        )

    def _get_profile_attr(self, obj, attr: str):
        profile = getattr(obj, "guest_profile", None)
        return getattr(profile, attr, "") if profile else ""

    def get_phone(self, obj) -> str:
        return str(obj.phone) if obj.phone else ""

    def get_address(self, obj) -> str:
        return self._get_profile_attr(obj, "address")

    def get_id_type(self, obj) -> str:
        return self._get_profile_attr(obj, "id_type")

    def get_id_number(self, obj) -> str:
        return self._get_profile_attr(obj, "id_number")


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    id_type = serializers.CharField(max_length=30, required=False, allow_blank=True)
    id_number = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def save(self, **kwargs):
        user = self.instance
        user_fields = ("first_name", "last_name", "email", "phone")
        profile_fields = ("address", "id_type", "id_number")

        user_updates = {
            f: self.validated_data[f] for f in user_fields if f in self.validated_data
        }
        profile_updates = {
            f: self.validated_data[f]
            for f in profile_fields
            if f in self.validated_data
        }

        if user_updates:
            for field, value in user_updates.items():
                setattr(user, field, value)
            user.save(update_fields=list(user_updates.keys()))

        if profile_updates:
            from reservations.models.guest import GuestProfile
            from reservations.services.guest_svc import update_guest_profile

            profile, created = GuestProfile.objects.get_or_create(user=user)
            if not created:
                update_guest_profile(profile, **profile_updates)
            else:
                for field, value in profile_updates.items():
                    setattr(profile, field, value)
                profile.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value: str) -> str:
        if len(value) < 8:
            raise serializers.ValidationError(
                "New password must be at least 8 characters."
            )
        return value
