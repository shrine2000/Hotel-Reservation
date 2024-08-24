import os

import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import logging

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
