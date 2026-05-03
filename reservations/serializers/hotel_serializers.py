from rest_framework import serializers

from reservations.models.hotel import Hotel


class HotelSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True, default=None)
    review_count = serializers.IntegerField(read_only=True, default=0)
    primary_photo = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = (
            "uid",
            "name",
            "location",
            "description",
            "star_rating",
            "avg_rating",
            "review_count",
            "primary_photo",
            "is_active",
            "created_at",
        )
        read_only_fields = ("uid", "is_active", "created_at")

    def get_primary_photo(self, obj: Hotel) -> str | None:
        photo = obj.photos.filter(is_primary=True).values("url").first()
        return photo["url"] if photo else None


class HotelDetailSerializer(HotelSerializer):
    rooms = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()

    class Meta(HotelSerializer.Meta):
        fields = HotelSerializer.Meta.fields + ("rooms", "photos", "recent_reviews")

    def get_rooms(self, obj: Hotel) -> list:
        from reservations.serializers.room_serializers import RoomSerializer

        rooms = obj.rooms.filter(is_active=True).order_by("base_cost")
        return RoomSerializer(rooms, many=True).data

    def get_photos(self, obj: Hotel) -> list:
        from reservations.serializers.hotel_photo_serializers import (
            HotelPhotoSerializer,
        )

        return HotelPhotoSerializer(obj.photos.all(), many=True).data

    def get_recent_reviews(self, obj: Hotel) -> list:
        from reservations.serializers.review_serializers import HotelReviewSerializer

        reviews = obj.reviews.select_related("user").order_by("-created_at")[:5]
        return HotelReviewSerializer(reviews, many=True).data


class HotelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ("name", "location", "description", "star_rating")

    def validate_name(self, value: str) -> str:
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return value.strip()

    def validate_star_rating(self, value: int) -> int:
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Star rating must be between 1 and 5.")
        return value


class HotelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ("name", "location", "description", "star_rating")
