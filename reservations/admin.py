from django.contrib import admin
from django.contrib.auth import get_user_model

from .models.guest import GuestProfile
from .models.hotel import Hotel
from .models.hotel_photo import HotelPhoto
from .models.payment import Payment
from .models.reservation import Reservation
from .models.review import HotelReview
from .models.room import Room


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "star_rating", "is_active")
    search_fields = ("name", "location")
    list_filter = ("star_rating", "is_active")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "hotel",
        "room_type",
        "luxury",
        "base_cost",
        "available_rooms",
        "max_guests",
    )
    list_filter = ("hotel", "room_type", "luxury")
    search_fields = ("hotel__name",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "room",
        "check_in_date",
        "number_of_days",
        "total_cost",
        "status",
        "is_active",
    )
    list_filter = ("status", "is_active")
    search_fields = ("user__username", "room__hotel__name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "uid",
        "reservation",
        "amount",
        "payment_method",
        "status",
        "created_at",
    )
    list_filter = ("status", "payment_method")
    search_fields = ("reference_id", "reservation__uid")


@admin.register(GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "id_type")
    search_fields = ("user__username", "phone")


@admin.register(HotelPhoto)
class HotelPhotoAdmin(admin.ModelAdmin):
    list_display = ("hotel", "url", "caption", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("hotel__name", "caption")


@admin.register(HotelReview)
class HotelReviewAdmin(admin.ModelAdmin):
    list_display = ("hotel", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("hotel__name", "user__username")


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "phone", "is_staff")
    search_fields = ("username", "email", "phone")
