from rest_framework import serializers

from reservations.models.guest import GuestProfile


class GuestProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = GuestProfile
        fields = (
            "uid",
            "username",
            "email",
            "phone",
            "address",
            "id_type",
            "id_number",
            "created_at",
        )
        read_only_fields = ("uid", "created_at")


class GuestProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestProfile
        fields = ("phone", "address", "id_type", "id_number")

    def validate_phone(self, value: str) -> str:
        cleaned = value.strip()
        if (
            cleaned
            and not cleaned.replace("+", "").replace("-", "").replace(" ", "").isdigit()
        ):
            raise serializers.ValidationError("Enter a valid phone number.")
        return cleaned

    def validate_id_number(self, value: str) -> str:
        return value.strip()


class GuestProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestProfile
        fields = ("phone", "address", "id_type", "id_number")

    def validate_phone(self, value: str) -> str:
        cleaned = value.strip()
        if (
            cleaned
            and not cleaned.replace("+", "").replace("-", "").replace(" ", "").isdigit()
        ):
            raise serializers.ValidationError("Enter a valid phone number.")
        return cleaned
