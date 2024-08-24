import pytest
from rest_framework import status


@pytest.mark.django_db
def test_login_success(api_client, create_user):
    url = "/api/login/"
    data = {
        "username": "testuser",
        "password": "testpassword",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_invalid_credentials(api_client, create_user):
    url = "/api/login/"
    data = {
        "username": "testuser",
        "password": "wrongpassword",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
