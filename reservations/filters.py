from datetime import timedelta

from django.db.models import (
    Count,
    ExpressionWrapper,
    F,
    DurationField,
    DateField,
    IntegerField,
)
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters

from reservations.enums import (
    PaymentMethod,
    PaymentStatus,
    ReservationStatus,
    RoomLuxury,
    RoomType,
)
from reservations.models.hotel import Hotel
from reservations.models.payment import Payment
from reservations.models.reservation import Reservation
from reservations.models.review import HotelReview
from reservations.models.room import Room


class HotelFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    location = filters.CharFilter(lookup_expr="icontains")
    star_rating = filters.NumberFilter()
    star_rating_min = filters.NumberFilter(field_name="star_rating", lookup_expr="gte")
    is_active = filters.BooleanFilter()

    class Meta:
        model = Hotel
        fields = ["name", "location", "star_rating", "is_active"]


class RoomFilter(filters.FilterSet):
    hotel = filters.CharFilter(field_name="hotel__uid")
    hotel_name = filters.CharFilter(field_name="hotel__name", lookup_expr="icontains")
    room_type = filters.ChoiceFilter(choices=RoomType.choices())
    luxury = filters.ChoiceFilter(choices=RoomLuxury.choices())
    min_price = filters.NumberFilter(field_name="base_cost", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="base_cost", lookup_expr="lte")
    max_guests = filters.NumberFilter(field_name="max_guests", lookup_expr="gte")
    amenity = filters.CharFilter(method="filter_amenity")
    available = filters.BooleanFilter(method="filter_available")
    check_in_date = filters.DateFilter(method="noop")
    number_of_days = filters.NumberFilter(method="noop")
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
            "max_guests",
            "amenity",
            "available",
            "is_active",
        ]

    def filter_available(self, queryset, name, value):
        if not value:
            return queryset
        check_in_str = self.data.get("check_in_date")
        days = self.data.get("number_of_days")
        if check_in_str and days:
            from datetime import date

            try:
                check_in = date.fromisoformat(check_in_str)
            except ValueError:
                return queryset
            return _filter_rooms_for_dates(queryset, check_in, int(days))
        return queryset.filter(available_rooms__gt=0)

    def filter_amenity(self, queryset, name, value):
        return queryset.filter(amenities__icontains=value)

    def noop(self, queryset, name, value):
        return queryset


def _filter_rooms_for_dates(queryset, check_in_date, number_of_days: int):
    """Return rooms with at least one slot available for the requested date range."""
    from reservations.enums import ReservationStatus as RS

    checkout_date = check_in_date + timedelta(days=number_of_days)
    active_statuses = [RS.PENDING.value, RS.CONFIRMED.value, RS.CHECKED_IN.value]

    stay = ExpressionWrapper(
        F("number_of_days") * timedelta(days=1), output_field=DurationField()
    )
    res_checkout_expr = ExpressionWrapper(
        F("check_in_date") + stay, output_field=DateField()
    )

    from django.db.models import OuterRef, Subquery

    overlapping_sq = Subquery(
        Reservation.objects.filter(
            room_id=OuterRef("pk"),
            status__in=active_statuses,
            is_active=True,
            check_in_date__lt=checkout_date,
        )
        .annotate(res_checkout=res_checkout_expr)
        .filter(res_checkout__gt=check_in_date)
        .values("room_id")
        .annotate(cnt=Count("pk"))
        .values("cnt")[:1],
        output_field=IntegerField(),
    )

    active_sq = Subquery(
        Reservation.objects.filter(
            room_id=OuterRef("pk"),
            status__in=active_statuses,
            is_active=True,
        )
        .values("room_id")
        .annotate(cnt=Count("pk"))
        .values("cnt")[:1],
        output_field=IntegerField(),
    )

    return (
        queryset.annotate(
            _overlapping=Coalesce(overlapping_sq, 0),
            _active=Coalesce(active_sq, 0),
        )
        .annotate(
            _future_available=ExpressionWrapper(
                F("available_rooms") + F("_active") - F("_overlapping"),
                output_field=IntegerField(),
            )
        )
        .filter(_future_available__gt=0)
    )


class ReservationFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=ReservationStatus.choices())
    check_in_from = filters.DateFilter(field_name="check_in_date", lookup_expr="gte")
    check_in_to = filters.DateFilter(field_name="check_in_date", lookup_expr="lte")
    room = filters.CharFilter(field_name="room__uid")
    upcoming = filters.BooleanFilter(method="filter_upcoming")
    is_active = filters.BooleanFilter()

    class Meta:
        model = Reservation
        fields = ["status", "check_in_from", "check_in_to", "room", "is_active"]

    def filter_upcoming(self, queryset, name, value):
        from datetime import date

        today = date.today()
        if value:
            return queryset.filter(
                check_in_date__gte=today,
                status__in=[
                    ReservationStatus.PENDING.value,
                    ReservationStatus.CONFIRMED.value,
                ],
            )
        return queryset.filter(
            status__in=[
                ReservationStatus.CHECKED_OUT.value,
                ReservationStatus.CANCELLED.value,
            ]
        )


class PaymentFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=PaymentStatus.choices())
    payment_method = filters.ChoiceFilter(choices=PaymentMethod.choices())
    reservation = filters.CharFilter(field_name="reservation__uid")

    class Meta:
        model = Payment
        fields = ["status", "payment_method", "reservation"]


class HotelReviewFilter(filters.FilterSet):
    hotel = filters.CharFilter(field_name="hotel__uid")
    rating = filters.NumberFilter()
    rating_min = filters.NumberFilter(field_name="rating", lookup_expr="gte")

    class Meta:
        model = HotelReview
        fields = ["hotel", "rating"]
