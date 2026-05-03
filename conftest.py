import os

os.environ.setdefault("PYTEST", "true")

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient
import logging

from reservations.models import Hotel
from reservations.models.room import Room
from reservations.models.reservation import Reservation
from reservations.enums import ReservationStatus

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_reservation.settings")

User = get_user_model()


@pytest.fixture(autouse=True)
def use_locmem_cache(settings):
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }


@pytest.fixture(scope="session", autouse=True)
def setup_initial_test_data(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        logger.info("Setting up initial test data for the database")


@pytest.fixture(scope="session")
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture(scope="session")
def admin_user():
    def _admin_user():
        return baker.make(
            User,
            is_superuser=True,
            is_staff=True,
            username="admin",
            email="admin@example.com",
        )

    return _admin_user


@pytest.fixture(scope="session")
def regular_user():
    def _regular_user():
        return baker.make(
            User,
            is_superuser=False,
            is_staff=False,
            username="user",
            email="user@example.com",
        )

    return _regular_user


@pytest.fixture(scope="session")
def hotel(admin_user):
    def _hotel():
        return baker.make(
            Hotel,
            name="Hotel Sunshine",
            location="Sunnydale",
            description="A lovely hotel in Sunnydale.",
            admin=admin_user(),
            is_active=True,
        )

    return _hotel


@pytest.fixture
def admin(db):
    return baker.make(User, is_staff=True, is_superuser=True)


@pytest.fixture
def guest(db):
    return baker.make(User, is_staff=False, is_superuser=False)


@pytest.fixture
def another_guest(db):
    return baker.make(User, is_staff=False, is_superuser=False)


@pytest.fixture
def admin_client(admin):
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def guest_client(guest):
    client = APIClient()
    client.force_authenticate(user=guest)
    return client


@pytest.fixture
def another_guest_client(another_guest):
    client = APIClient()
    client.force_authenticate(user=another_guest)
    return client


@pytest.fixture
def hotel_obj(admin):
    return baker.make(
        Hotel,
        admin=admin,
        name="Grand Hotel",
        location="Mumbai",
        description="A test hotel",
        star_rating=4,
        is_active=True,
    )


@pytest.fixture
def room_obj(hotel_obj):
    return baker.make(
        Room,
        hotel=hotel_obj,
        room_type="S",
        luxury="D",
        base_cost=Decimal("1500.00"),
        available_rooms=5,
        max_guests=2,
        is_active=True,
    )


@pytest.fixture
def pending_reservation(guest, room_obj):
    return baker.make(
        Reservation,
        user=guest,
        room=room_obj,
        check_in_date=date.today() + timedelta(days=1),
        number_of_days=3,
        total_cost=Decimal("4500.00"),
        status=ReservationStatus.PENDING.value,
        is_active=True,
    )


@pytest.fixture
def confirmed_reservation(guest, room_obj):
    return baker.make(
        Reservation,
        user=guest,
        room=room_obj,
        check_in_date=date.today() + timedelta(days=1),
        number_of_days=3,
        total_cost=Decimal("4500.00"),
        status=ReservationStatus.CONFIRMED.value,
        is_active=True,
    )


@pytest.fixture
def checkedin_reservation(guest, room_obj):
    return baker.make(
        Reservation,
        user=guest,
        room=room_obj,
        check_in_date=date.today() + timedelta(days=1),
        number_of_days=3,
        total_cost=Decimal("4500.00"),
        status=ReservationStatus.CHECKED_IN.value,
        is_active=True,
    )
