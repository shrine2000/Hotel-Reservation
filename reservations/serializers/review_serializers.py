from rest_framework import serializers

from reservations.models.hotel import Hotel
from reservations.models.review import HotelReview


class HotelReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    hotel_uid = serializers.CharField(source="hotel.uid", read_only=True)

    class Meta:
        model = HotelReview
        fields = (
            "uid",
            "hotel_uid",
            "username",
            "rating",
            "comment",
            "created_at",
            "last_updated_at",
        )
        read_only_fields = ("uid", "created_at", "last_updated_at")


class HotelReviewCreateSerializer(serializers.Serializer):
    class Meta:
        model = HotelReview

    hotel_uid = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_hotel_uid(self, value) -> Hotel:
        try:
            return Hotel.objects.only("uid", "id", "is_active").get(
                uid=value, is_active=True
            )
        except Hotel.DoesNotExist:
            raise serializers.ValidationError("Hotel not found.")


class HotelReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelReview
        fields = ("rating", "comment")

    def validate_rating(self, value: int) -> int:
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
