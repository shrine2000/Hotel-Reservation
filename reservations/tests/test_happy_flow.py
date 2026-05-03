from datetime import date, timedelta
from decimal import Decimal

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from reservations.enums import PaymentStatus, ReservationStatus
from reservations.models.payment import Payment

BASE = "/api"


@pytest.mark.django_db
def test_register_creates_user():
    client = APIClient()
    response = client.post(
        f"{BASE}/register/",
        {
            "username": "newuser",
            "password": "Secret@123",
            "email": "newuser@test.com",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == "newuser"
    assert "password" not in response.data


@pytest.mark.django_db
def test_login_returns_jwt_tokens(guest):
    guest.set_password("Secret@123")
    guest.save()
    client = APIClient()
    response = client.post(
        f"{BASE}/login/",
        {
            "username": guest.username,
            "password": "Secret@123",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_invalid_credentials_returns_401():
    client = APIClient()
    response = client.post(
        f"{BASE}/login/",
        {
            "username": "nobody",
            "password": "wrong",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_admin_creates_hotel(admin_client):
    response = admin_client.post(
        f"{BASE}/hotels/",
        {
            "name": "Palace Hotel",
            "location": "Delhi",
            "description": "A luxury hotel",
            "star_rating": 5,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Palace Hotel"
    assert response.data["uid"]


@pytest.mark.django_db
def test_guest_cannot_create_hotel(guest_client):
    response = guest_client.post(
        f"{BASE}/hotels/",
        {
            "name": "Cheap Inn",
            "location": "Goa",
            "description": "Budget stay",
            "star_rating": 2,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_hotels_returns_active_hotels(guest_client, hotel_obj):
    response = guest_client.get(f"{BASE}/hotels/")
    assert response.status_code == status.HTTP_200_OK
    uids = [h["uid"] for h in response.data["results"]]
    assert str(hotel_obj.uid) in uids


@pytest.mark.django_db
def test_hotel_detail_includes_expected_fields(guest_client, hotel_obj):
    response = guest_client.get(f"{BASE}/hotels/{hotel_obj.uid}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == hotel_obj.name
    assert response.data["location"] == hotel_obj.location
    assert "avg_rating" in response.data


@pytest.mark.django_db
def test_admin_updates_hotel(admin_client, hotel_obj):
    response = admin_client.patch(
        f"{BASE}/hotels/{hotel_obj.uid}/",
        {
            "description": "Updated description",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["description"] == "Updated description"


@pytest.mark.django_db
def test_admin_deactivates_hotel(admin_client, hotel_obj):
    response = admin_client.patch(f"{BASE}/hotels/{hotel_obj.uid}/deactivate/")
    assert response.status_code == status.HTTP_200_OK
    hotel_obj.refresh_from_db()
    assert not hotel_obj.is_active


@pytest.mark.django_db
def test_admin_creates_room(admin_client, hotel_obj):
    response = admin_client.post(
        f"{BASE}/rooms/",
        {
            "hotel_uid": hotel_obj.uid,
            "room_type": "S",
            "luxury": "D",
            "base_cost": "1200.00",
            "available_rooms": 10,
            "max_guests": 2,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["uid"]
    assert response.data["room_type"] == "S"


@pytest.mark.django_db
def test_guest_cannot_create_room(guest_client, hotel_obj):
    response = guest_client.post(
        f"{BASE}/rooms/",
        {
            "hotel_uid": hotel_obj.uid,
            "room_type": "D",
            "luxury": "D",
            "base_cost": "800.00",
            "available_rooms": 5,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_rooms_filtered_by_hotel(guest_client, room_obj):
    response = guest_client.get(f"{BASE}/rooms/", {"hotel": room_obj.hotel.uid})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 1
    assert all(
        r["hotel_uid"] == str(room_obj.hotel.uid) for r in response.data["results"]
    )


@pytest.mark.django_db
def test_availability_filter_returns_rooms(guest_client, room_obj):
    tomorrow = date.today() + timedelta(days=1)
    response = guest_client.get(
        f"{BASE}/rooms/",
        {
            "available": "true",
            "check_in_date": str(tomorrow),
            "number_of_days": 2,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    uids = [r["uid"] for r in response.data["results"]]
    assert str(room_obj.uid) in uids


@pytest.mark.django_db
def test_guest_creates_profile(guest_client):
    response = guest_client.post(
        f"{BASE}/guests/",
        {
            "id_type": "PASSPORT",
            "id_number": "X9876543",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["uid"]
    assert response.data["id_type"] == "PASSPORT"


@pytest.mark.django_db
def test_duplicate_profile_returns_409(guest_client):
    guest_client.post(
        f"{BASE}/guests/",
        {"id_type": "PASSPORT", "id_number": "X9876543"},
        format="json",
    )
    response = guest_client.post(
        f"{BASE}/guests/",
        {"id_type": "PASSPORT", "id_number": "X9876543"},
        format="json",
    )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_guest_updates_own_profile(guest_client):
    create = guest_client.post(
        f"{BASE}/guests/",
        {
            "id_type": "PASSPORT",
            "id_number": "X9876543",
        },
        format="json",
    )
    uid = create.data["uid"]
    response = guest_client.patch(
        f"{BASE}/guests/{uid}/",
        {
            "address": "123 Main Street",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["address"] == "123 Main Street"


@pytest.mark.django_db
def test_idor_guest_profile_not_visible_to_another_user(
    guest_client, another_guest_client
):
    create = guest_client.post(
        f"{BASE}/guests/",
        {"id_type": "PASSPORT", "id_number": "X9876543"},
        format="json",
    )
    uid = create.data["uid"]
    response = another_guest_client.get(f"{BASE}/guests/{uid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_guest_creates_reservation(guest_client, room_obj):
    tomorrow = str(date.today() + timedelta(days=1))
    response = guest_client.post(
        f"{BASE}/reservations/",
        {
            "room_uid": room_obj.uid,
            "check_in_date": tomorrow,
            "number_of_days": 2,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["uid"]
    assert response.data["status"] == ReservationStatus.PENDING.value
    assert Decimal(response.data["total_cost"]) == room_obj.base_cost * 2


@pytest.mark.django_db
def test_reservation_decrements_available_rooms(guest_client, room_obj):
    before = room_obj.available_rooms
    tomorrow = str(date.today() + timedelta(days=1))
    guest_client.post(
        f"{BASE}/reservations/",
        {
            "room_uid": room_obj.uid,
            "check_in_date": tomorrow,
            "number_of_days": 1,
        },
        format="json",
    )
    room_obj.refresh_from_db()
    assert room_obj.available_rooms == before - 1


@pytest.mark.django_db
def test_admin_confirms_reservation(admin_client, guest_client, pending_reservation):
    guest_client.force_authenticate(user=pending_reservation.user)
    response = admin_client.post(
        f"{BASE}/reservations/{pending_reservation.uid}/confirm/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == ReservationStatus.CONFIRMED.value


@pytest.mark.django_db
def test_admin_checks_in_reservation(admin_client, confirmed_reservation):
    response = admin_client.post(
        f"{BASE}/reservations/{confirmed_reservation.uid}/check-in/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == ReservationStatus.CHECKED_IN.value


@pytest.mark.django_db
def test_admin_checks_out_reservation(admin_client, checkedin_reservation, room_obj):
    before = room_obj.available_rooms
    response = admin_client.post(
        f"{BASE}/reservations/{checkedin_reservation.uid}/check-out/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == ReservationStatus.CHECKED_OUT.value
    room_obj.refresh_from_db()
    assert room_obj.available_rooms == before + 1


@pytest.mark.django_db
def test_guest_cancels_pending_reservation(guest_client, pending_reservation, room_obj):
    guest_client.force_authenticate(user=pending_reservation.user)
    before = room_obj.available_rooms
    response = guest_client.post(
        f"{BASE}/reservations/{pending_reservation.uid}/cancel/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == ReservationStatus.CANCELLED.value
    room_obj.refresh_from_db()
    assert room_obj.available_rooms == before + 1


@pytest.mark.django_db
def test_idor_reservation_not_visible_to_another_user(
    another_guest_client, pending_reservation
):
    response = another_guest_client.get(
        f"{BASE}/reservations/{pending_reservation.uid}/"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_guest_creates_payment(guest_client, confirmed_reservation):
    guest_client.force_authenticate(user=confirmed_reservation.user)
    response = guest_client.post(
        f"{BASE}/payments/",
        {
            "reservation_uid": confirmed_reservation.uid,
            "amount": "4500.00",
            "payment_method": "CC",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["uid"]
    assert response.data["status"] == PaymentStatus.COMPLETED.value


@pytest.mark.django_db
def test_payment_auto_confirms_pending_reservation(guest_client, pending_reservation):
    guest_client.force_authenticate(user=pending_reservation.user)
    guest_client.post(
        f"{BASE}/payments/",
        {
            "reservation_uid": pending_reservation.uid,
            "amount": "4500.00",
            "payment_method": "CA",
        },
        format="json",
    )
    pending_reservation.refresh_from_db()
    assert pending_reservation.status == ReservationStatus.CONFIRMED.value


@pytest.mark.django_db
def test_duplicate_payment_returns_409(guest_client, confirmed_reservation):
    guest_client.force_authenticate(user=confirmed_reservation.user)
    payload = {
        "reservation_uid": confirmed_reservation.uid,
        "amount": "4500.00",
        "payment_method": "CC",
    }
    guest_client.post(f"{BASE}/payments/", payload, format="json")
    response = guest_client.post(f"{BASE}/payments/", payload, format="json")
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_idor_payment_not_visible_to_another_user(
    another_guest_client, confirmed_reservation
):
    payment = baker.make(
        Payment,
        reservation=confirmed_reservation,
        amount=Decimal("4500.00"),
        payment_method="CC",
        status=PaymentStatus.COMPLETED.value,
    )
    response = another_guest_client.get(f"{BASE}/payments/{payment.uid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_guest_creates_review(guest_client, hotel_obj):
    response = guest_client.post(
        f"{BASE}/reviews/",
        {
            "hotel_uid": hotel_obj.uid,
            "rating": 5,
            "comment": "Excellent stay!",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["uid"]
    assert response.data["rating"] == 5


@pytest.mark.django_db
def test_guest_updates_own_review(guest_client, hotel_obj):
    create = guest_client.post(
        f"{BASE}/reviews/",
        {
            "hotel_uid": hotel_obj.uid,
            "rating": 5,
            "comment": "Great!",
        },
        format="json",
    )
    uid = create.data["uid"]
    response = guest_client.patch(
        f"{BASE}/reviews/{uid}/",
        {
            "rating": 3,
            "comment": "It was okay.",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["rating"] == 3


@pytest.mark.django_db
def test_upsert_prevents_duplicate_review(guest_client, hotel_obj):
    guest_client.post(
        f"{BASE}/reviews/",
        {"hotel_uid": hotel_obj.uid, "rating": 5, "comment": "First"},
        format="json",
    )
    guest_client.post(
        f"{BASE}/reviews/",
        {"hotel_uid": hotel_obj.uid, "rating": 4, "comment": "Second"},
        format="json",
    )
    response = guest_client.get(f"{BASE}/reviews/", {"hotel": hotel_obj.uid})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["rating"] == 4


@pytest.mark.django_db
def test_anyone_can_list_reviews(guest_client, hotel_obj):
    guest_client.post(
        f"{BASE}/reviews/",
        {"hotel_uid": hotel_obj.uid, "rating": 4, "comment": "Good"},
        format="json",
    )
    response = guest_client.get(f"{BASE}/reviews/", {"hotel": hotel_obj.uid})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_admin_creates_hotel_photo(admin_client, hotel_obj):
    response = admin_client.post(
        f"{BASE}/hotel-photos/",
        {
            "hotel_uid": hotel_obj.uid,
            "url": "https://example.com/lobby.jpg",
            "caption": "Hotel lobby",
            "is_primary": True,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["uid"]
    assert response.data["is_primary"] is True


@pytest.mark.django_db
def test_only_one_primary_photo_per_hotel(admin_client, hotel_obj):
    admin_client.post(
        f"{BASE}/hotel-photos/",
        {
            "hotel_uid": hotel_obj.uid,
            "url": "https://example.com/first.jpg",
            "is_primary": True,
        },
        format="json",
    )
    admin_client.post(
        f"{BASE}/hotel-photos/",
        {
            "hotel_uid": hotel_obj.uid,
            "url": "https://example.com/second.jpg",
            "is_primary": True,
        },
        format="json",
    )
    response = admin_client.get(f"{BASE}/hotel-photos/", {"hotel": hotel_obj.uid})
    primary_photos = [p for p in response.data["results"] if p["is_primary"]]
    assert len(primary_photos) == 1
    assert primary_photos[0]["url"] == "https://example.com/second.jpg"
