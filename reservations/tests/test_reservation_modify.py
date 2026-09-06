from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from reservations.enums import ReservationStatus

BASE = "/api"


@pytest.mark.django_db
def test_modify_pending_reservation_updates_cost(guest_client, pending_reservation):
    url = f"{BASE}/reservations/{pending_reservation.uid}/modify/"
    response = guest_client.patch(url, {"number_of_days": 5}, format="json")
    assert response.status_code == status.HTTP_200_OK
    pending_reservation.refresh_from_db()
    assert pending_reservation.number_of_days == 5
    assert pending_reservation.total_cost == pending_reservation.room.base_cost * 5


@pytest.mark.django_db
def test_modify_reservation_check_in_date(guest_client, pending_reservation):
    new_date = date.today() + timedelta(days=10)
    url = f"{BASE}/reservations/{pending_reservation.uid}/modify/"
    response = guest_client.patch(
        url, {"check_in_date": new_date.isoformat()}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    pending_reservation.refresh_from_db()
    assert str(pending_reservation.check_in_date) == new_date.isoformat()


@pytest.mark.django_db
def test_modify_reservation_requires_a_field(guest_client, pending_reservation):
    url = f"{BASE}/reservations/{pending_reservation.uid}/modify/"
    response = guest_client.patch(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_modify_reservation_rejects_past_date(guest_client, pending_reservation):
    url = f"{BASE}/reservations/{pending_reservation.uid}/modify/"
    response = guest_client.patch(
        url,
        {"check_in_date": (date.today() - timedelta(days=1)).isoformat()},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_modify_checked_in_reservation_fails(guest_client, checkedin_reservation):
    url = f"{BASE}/reservations/{checkedin_reservation.uid}/modify/"
    response = guest_client.patch(url, {"number_of_days": 5}, format="json")
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_modify_other_users_reservation_not_found(
    another_guest_client, pending_reservation
):
    url = f"{BASE}/reservations/{pending_reservation.uid}/modify/"
    response = another_guest_client.patch(url, {"number_of_days": 5}, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_modify_confirmed_reservation(guest, room_obj):
    from model_bakery import baker

    from reservations.models.reservation import Reservation

    reservation = baker.make(
        Reservation,
        user=guest,
        room=room_obj,
        check_in_date=date.today() + timedelta(days=2),
        number_of_days=2,
        total_cost=room_obj.base_cost * 2,
        status=ReservationStatus.CONFIRMED.value,
        is_active=True,
    )
    client = APIClient()
    client.force_authenticate(user=guest)
    url = f"{BASE}/reservations/{reservation.uid}/modify/"
    response = client.patch(url, {"number_of_days": 4}, format="json")
    assert response.status_code == status.HTTP_200_OK
    reservation.refresh_from_db()
    assert reservation.total_cost == room_obj.base_cost * 4
