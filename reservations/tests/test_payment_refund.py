from decimal import Decimal

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from reservations.enums import PaymentStatus
from reservations.models.payment import Payment

BASE = "/api"


@pytest.mark.django_db
def test_guest_refunds_completed_payment(guest_client, confirmed_reservation):
    guest_client.force_authenticate(user=confirmed_reservation.user)
    payment = baker.make(
        Payment,
        reservation=confirmed_reservation,
        amount=Decimal("4500.00"),
        payment_method="CC",
        status=PaymentStatus.COMPLETED.value,
    )
    response = guest_client.post(f"{BASE}/payments/{payment.uid}/refund/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == PaymentStatus.REFUNDED.value
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.REFUNDED.value


@pytest.mark.django_db
def test_double_refund_returns_409(guest_client, confirmed_reservation):
    guest_client.force_authenticate(user=confirmed_reservation.user)
    payment = baker.make(
        Payment,
        reservation=confirmed_reservation,
        amount=Decimal("4500.00"),
        payment_method="CC",
        status=PaymentStatus.REFUNDED.value,
    )
    response = guest_client.post(f"{BASE}/payments/{payment.uid}/refund/")
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_refund_other_users_payment_not_found(
    another_guest_client, confirmed_reservation
):
    payment = baker.make(
        Payment,
        reservation=confirmed_reservation,
        amount=Decimal("4500.00"),
        payment_method="CC",
        status=PaymentStatus.COMPLETED.value,
    )
    response = another_guest_client.post(f"{BASE}/payments/{payment.uid}/refund/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_refund_requires_authentication(confirmed_reservation):
    payment = baker.make(
        Payment,
        reservation=confirmed_reservation,
        amount=Decimal("4500.00"),
        payment_method="CC",
        status=PaymentStatus.COMPLETED.value,
    )
    response = APIClient().post(f"{BASE}/payments/{payment.uid}/refund/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_staff_can_refund_guest_payment(admin_client, confirmed_reservation):
    payment = baker.make(
        Payment,
        reservation=confirmed_reservation,
        amount=Decimal("4500.00"),
        payment_method="CC",
        status=PaymentStatus.COMPLETED.value,
    )
    response = admin_client.post(f"{BASE}/payments/{payment.uid}/refund/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == PaymentStatus.REFUNDED.value
