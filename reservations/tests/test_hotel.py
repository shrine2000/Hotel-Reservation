import pytest
from rest_framework import status


@pytest.mark.django_db
def test_hotel_list_view(api_client, regular_user, hotel):
    regular_user = regular_user()
    hotel = hotel()
    api_client.force_authenticate(user=regular_user)
    response = api_client.get("/api/hotels/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] > 0
    assert response.data["results"][0]["name"] == hotel.name


@pytest.mark.django_db
def test_hotel_detail_view(api_client, regular_user, hotel, admin_user):
    regular_user = regular_user()
    hotel = hotel()
    api_client.force_authenticate(user=regular_user)
    response = api_client.get(f"/api/hotels/{hotel.uid}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == hotel.name


@pytest.mark.django_db
def test_hotel_create_view_permission(api_client, regular_user):
    regular_user = regular_user()
    api_client.force_authenticate(user=regular_user)
    data = {"name": "New Hotel", "is_active": True}
    response = api_client.post("/api/hotels/", data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_hotel_update_view_permission(api_client, regular_user, hotel):
    regular_user = regular_user()
    hotel = hotel()
    api_client.force_authenticate(user=regular_user)
    data = {"name": "Updated Hotel"}
    response = api_client.put(f"/api/hotels/{hotel.uid}/", data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_hotel_deactivate_view_permission(api_client, regular_user, hotel):
    regular_user = regular_user()
    hotel = hotel()
    api_client.force_authenticate(user=regular_user)
    response = api_client.patch(f"/api/hotels/{hotel.uid}/deactivate/", format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN
