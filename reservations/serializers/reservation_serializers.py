from datetime import date

from rest_framework import serializers

from reservations.models.reservation import Reservation
from reservations.models.room import Room


class ReservationSerializer(serializers.ModelSerializer):
    room_uid = serializers.CharField(source="room.uid", read_only=True)
    room_type = serializers.CharField(source="room.room_type", read_only=True)
    room_luxury = serializers.CharField(source="room.luxury", read_only=True)
    hotel_name = serializers.CharField(source="room.hotel.name", read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "uid",
            "room_uid",
            "room_type",
            "room_luxury",
            "hotel_name",
            "check_in_date",
            "number_of_days",
            "total_cost",
            "status",
            "is_active",
            "created_at",
        )
        read_only_fields = ("uid", "total_cost", "status", "is_active", "created_at")


class ReservationCreateSerializer(serializers.Serializer):
    class Meta:
        model = Reservation

    room_uid = serializers.CharField()
    check_in_date = serializers.DateField()
    number_of_days = serializers.IntegerField(min_value=1, max_value=365)

    def validate_room_uid(self, value) -> Room:
        try:
            return Room.objects.only(
                "uid", "id", "base_cost", "available_rooms", "is_active"
            ).get(uid=value, is_active=True)
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room not found or unavailable.")

    def validate_check_in_date(self, value: date) -> date:
        if value < date.today():
            raise serializers.ValidationError("Check-in date cannot be in the past.")
        return value


class ReservationModifySerializer(serializers.Serializer):
    class Meta:
        model = Reservation

    check_in_date = serializers.DateField(required=False)
    number_of_days = serializers.IntegerField(
        min_value=1, max_value=365, required=False
    )

    def validate(self, attrs: dict) -> dict:
        if not attrs:
            raise serializers.ValidationError(
                "Provide at least check_in_date or number_of_days to modify."
            )
        return attrs

    def validate_check_in_date(self, value: date) -> date:
        if value < date.today():
            raise serializers.ValidationError("Check-in date cannot be in the past.")
        return value
