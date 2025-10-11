from django_filters import rest_framework as filters
from reservations.models.hotel import Hotel
from reservations.models.room import Room


class HotelFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    location = filters.CharFilter(lookup_expr="icontains")
    admin = filters.UUIDFilter(field_name="admin__id")
    is_active = filters.BooleanFilter()

    class Meta:
        model = Hotel
        fields = ["name", "location", "admin", "is_active"]


class RoomFilter(filters.FilterSet):
    hotel = filters.UUIDFilter(field_name="hotel__uid")
    hotel_name = filters.CharFilter(field_name="hotel__name", lookup_expr="icontains")
    room_type = filters.ChoiceFilter(choices=[("S", "Single"), ("D", "Double")])
    luxury = filters.ChoiceFilter(choices=[("D", "Deluxe"), ("SD", "Super Deluxe")])
    min_price = filters.NumberFilter(field_name="base_cost", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="base_cost", lookup_expr="lte")
    available = filters.BooleanFilter(method="filter_available")
    is_active = filters.BooleanFilter()

    class Meta:
        model = Room
        fields = [
            "hotel",
            "hotel_name",
            "room_type",
            "luxury",
            "min_price",
            "max_price",
            "is_active",
        ]

    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(available_rooms__gt=0)
        return queryset
