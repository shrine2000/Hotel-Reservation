from datetime import date

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F

from reservations.enums import ReservationStatus
from reservations.exceptions import (
    CheckInDateInPastError,
    InvalidReservationStatusTransitionError,
    NoRoomsAvailableError,
    ReservationNotCancellableError,
)
from reservations.models.reservation import Reservation
from reservations.models.room import Room

User = get_user_model()

_CANCELLABLE = {ReservationStatus.PENDING.value, ReservationStatus.CONFIRMED.value}
_MODIFIABLE = {ReservationStatus.PENDING.value, ReservationStatus.CONFIRMED.value}


def create_reservation(
    user,
    room: Room,
    check_in_date: date,
    number_of_days: int,
) -> Reservation:
    if check_in_date < date.today():
        raise CheckInDateInPastError()

    with transaction.atomic():
        locked_room = Room.objects.select_for_update().get(pk=room.pk)
        if locked_room.available_rooms < 1:
            raise NoRoomsAvailableError()
        locked_room.available_rooms -= 1
        locked_room.save(update_fields=["available_rooms"])
        reservation = Reservation.objects.create(
            user=user,
            room=locked_room,
            check_in_date=check_in_date,
            number_of_days=number_of_days,
            total_cost=locked_room.base_cost * number_of_days,
            status=ReservationStatus.PENDING.value,
        )
    return reservation


def confirm_reservation(reservation: Reservation) -> Reservation:
    if reservation.status != ReservationStatus.PENDING.value:
        raise InvalidReservationStatusTransitionError()
    reservation.status = ReservationStatus.CONFIRMED.value
    reservation.save(update_fields=["status"])
    return reservation


def check_in_reservation(reservation: Reservation) -> Reservation:
    if reservation.status != ReservationStatus.CONFIRMED.value:
        raise InvalidReservationStatusTransitionError()
    reservation.status = ReservationStatus.CHECKED_IN.value
    reservation.save(update_fields=["status"])
    return reservation


def check_out_reservation(reservation: Reservation) -> Reservation:
    if reservation.status != ReservationStatus.CHECKED_IN.value:
        raise InvalidReservationStatusTransitionError()
    with transaction.atomic():
        Room.objects.filter(pk=reservation.room_id).update(
            available_rooms=F("available_rooms") + 1
        )
        reservation.status = ReservationStatus.CHECKED_OUT.value
        reservation.is_active = False
        reservation.save(update_fields=["status", "is_active"])
    return reservation


def cancel_reservation(reservation: Reservation) -> Reservation:
    if reservation.status not in _CANCELLABLE:
        raise ReservationNotCancellableError()
    with transaction.atomic():
        Room.objects.filter(pk=reservation.room_id).update(
            available_rooms=F("available_rooms") + 1
        )
        reservation.status = ReservationStatus.CANCELLED.value
        reservation.is_active = False
        reservation.save(update_fields=["status", "is_active"])
    return reservation


def modify_reservation(
    reservation: Reservation,
    check_in_date: date | None = None,
    number_of_days: int | None = None,
) -> Reservation:
    if reservation.status not in _MODIFIABLE:
        raise InvalidReservationStatusTransitionError()

    new_check_in = check_in_date or reservation.check_in_date
    new_days = number_of_days or reservation.number_of_days

    if new_check_in < date.today():
        raise CheckInDateInPastError()

    reservation.check_in_date = new_check_in
    reservation.number_of_days = new_days
    reservation.total_cost = reservation.room.base_cost * new_days
    reservation.save(update_fields=["check_in_date", "number_of_days", "total_cost"])
    return reservation
