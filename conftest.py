import os

import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import logging
from model_bakery import baker

from reservations.models import Hotel

logger = logging.getLogger(__name__)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_reservation.settings")


@pytest.fixture(scope="session", autouse=True)
def setup_initial_test_data(django_db_setup, django_db_blocker):
    # this could be useful in future when loading initial data, custom migrations, setting up test specific configs
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
            password="adminpassword",
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
            password="userpassword",
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
            admin=admin_user,
            is_active=True,
        )

    return _hotel
