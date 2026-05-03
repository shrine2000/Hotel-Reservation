import os

os.environ.setdefault("PYTEST", "true")

import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient
import logging

from reservations.models import Hotel

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
