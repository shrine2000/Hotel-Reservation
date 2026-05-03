from rest_framework import serializers

from reservations.enums import RoomLuxury, RoomType
from reservations.models.hotel import Hotel
from reservations.models.room import Room


class RoomSerializer(serializers.ModelSerializer):
    hotel_uid = serializers.CharField(source="hotel.uid", read_only=True)
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)

    class Meta:
        model = Room
        fields = (
            "uid",
            "hotel_uid",
            "hotel_name",
            "room_type",
            "luxury",
            "base_cost",
            "available_rooms",
            "max_guests",
            "amenities",
            "is_active",
            "created_at",
        )
        read_only_fields = ("uid", "created_at")


class RoomCreateSerializer(serializers.ModelSerializer):
    hotel_uid = serializers.CharField(write_only=True)

    class Meta:
        model = Room
        fields = (
            "hotel_uid",
            "room_type",
            "luxury",
            "base_cost",
            "available_rooms",
            "max_guests",
            "amenities",
        )

    def validate_room_type(self, value: str) -> str:
        if value not in RoomType.values():
            raise serializers.ValidationError(
                f"Invalid room type. Choices: {RoomType.values()}"
            )
        return value

    def validate_luxury(self, value: str) -> str:
        if value not in RoomLuxury.values():
            raise serializers.ValidationError(
                f"Invalid luxury level. Choices: {RoomLuxury.values()}"
            )
        return value

    def validate_base_cost(self, value) -> float:
        if value <= 0:
            raise serializers.ValidationError("Base cost must be greater than zero.")
        return value

    def validate_available_rooms(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError("Available rooms cannot be negative.")
        return value

    def validate_hotel_uid(self, value) -> Hotel:
        try:
            return Hotel.objects.get(uid=value, is_active=True)
        except Hotel.DoesNotExist:
            raise serializers.ValidationError("Hotel not found or inactive.")

    def validate_amenities(self, value) -> list:
        if not isinstance(value, list):
            raise serializers.ValidationError("Amenities must be a list of strings.")
        cleaned = [str(a).strip() for a in value if str(a).strip()]
        return cleaned

    def create(self, validated_data: dict) -> Room:
        hotel = validated_data.pop("hotel_uid")
        return Room.objects.create(hotel=hotel, **validated_data)


class RoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("base_cost", "available_rooms", "max_guests", "amenities")

    def validate_base_cost(self, value) -> float:
        if value <= 0:
            raise serializers.ValidationError("Base cost must be greater than zero.")
        return value

    def validate_available_rooms(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError("Available rooms cannot be negative.")
        return value

    def validate_amenities(self, value) -> list:
        if not isinstance(value, list):
            raise serializers.ValidationError("Amenities must be a list of strings.")
        return [str(a).strip() for a in value if str(a).strip()]
