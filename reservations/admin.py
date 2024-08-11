from django.contrib import admin
from .models.hotel import Hotel
from .models.reservation import Reservation
from .models.room import Room


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active")
    search_fields = ("name", "location")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("hotel", "room_type", "luxury", "base_cost", "available_rooms")
    list_filter = ("hotel", "room_type", "luxury")
    search_fields = ("hotel__name", "room_type", "luxury")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "room",
        "check_in_date",
        "number_of_days",
        "total_cost",
        "is_active",
    )
    list_filter = ("user", "room", "check_in_date")
    search_fields = ("user__username", "room__hotel__name")
