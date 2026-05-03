from rest_framework import serializers

from reservations.models.hotel import Hotel
from reservations.models.hotel_photo import HotelPhoto


class HotelPhotoSerializer(serializers.ModelSerializer):
    hotel_uid = serializers.CharField(source="hotel.uid", read_only=True)

    class Meta:
        model = HotelPhoto
        fields = ("uid", "hotel_uid", "url", "caption", "is_primary", "created_at")
        read_only_fields = ("uid", "created_at")


class HotelPhotoCreateSerializer(serializers.Serializer):
    class Meta:
        model = HotelPhoto

    hotel_uid = serializers.CharField()
    url = serializers.URLField(max_length=500)
    caption = serializers.CharField(
        max_length=200, required=False, default="", allow_blank=True
    )
    is_primary = serializers.BooleanField(required=False, default=False)

    def validate_hotel_uid(self, value) -> Hotel:
        try:
            return Hotel.objects.only("uid", "id", "is_active", "admin_id").get(
                uid=value, is_active=True
            )
        except Hotel.DoesNotExist:
            raise serializers.ValidationError("Hotel not found.")
