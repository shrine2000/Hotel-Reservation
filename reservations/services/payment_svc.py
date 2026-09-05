from decimal import Decimal

from reservations.enums import PaymentStatus, ReservationStatus
from reservations.exceptions import (
    PaymentAlreadyCompletedError,
    PaymentNotRefundableError,
)
from reservations.models.payment import Payment
from reservations.models.reservation import Reservation


def create_payment(
    reservation: Reservation,
    amount: Decimal,
    payment_method: str,
    reference_id: str = "",
    notes: str = "",
) -> Payment:
    if Payment.objects.filter(
        reservation=reservation, status=PaymentStatus.COMPLETED.value
    ).exists():
        raise PaymentAlreadyCompletedError()

    payment = Payment.objects.create(
        reservation=reservation,
        amount=amount,
        payment_method=payment_method,
        status=PaymentStatus.COMPLETED.value,
        reference_id=reference_id,
        notes=notes,
    )
    if reservation.status == ReservationStatus.PENDING.value:
        from reservations.services import reservation_svc

        reservation_svc.confirm_reservation(reservation)
    return payment


def refund_payment(payment: Payment) -> Payment:
    if payment.status != PaymentStatus.COMPLETED.value:
        raise PaymentNotRefundableError()
    payment.status = PaymentStatus.REFUNDED.value
    payment.save(update_fields=["status"])
    return payment
