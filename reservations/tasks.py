import logging
from collections import defaultdict
from datetime import date, timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import DateField, DurationField, ExpressionWrapper, F

from reservations.enums import ReservationStatus
from reservations.models.reservation import Reservation
from reservations.models.room import Room

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300, ignore_result=True)
def release_expired_reservations(self) -> None:
    today = date.today()

    stay_duration = ExpressionWrapper(
        F("number_of_days") * timedelta(days=1),
        output_field=DurationField(),
    )
    checkout_date = ExpressionWrapper(
        F("check_in_date") + stay_duration,
        output_field=DateField(),
    )

    active_statuses = [
        ReservationStatus.PENDING.value,
        ReservationStatus.CONFIRMED.value,
        ReservationStatus.CHECKED_IN.value,
    ]

    expired = list(
        Reservation.objects.using("replica")
        .filter(is_active=True, status__in=active_statuses)
        .annotate(checkout_date=checkout_date)
        .filter(checkout_date__lte=today)
        .select_related("room")
        .only("id", "room_id", "status", "is_active")
    )

    if not expired:
        logger.info("No expired reservations to release")
        return

    room_increments: dict[int, int] = defaultdict(int)
    for reservation in expired:
        room_increments[reservation.room_id] += 1

    expired_ids = [r.id for r in expired]

    try:
        with transaction.atomic():
            for room_id, increment in room_increments.items():
                Room.objects.filter(id=room_id).update(
                    available_rooms=F("available_rooms") + increment
                )
            Reservation.objects.filter(id__in=expired_ids).update(
                is_active=False,
                status=ReservationStatus.CHECKED_OUT.value,
            )
    except Exception as exc:
        logger.warning(
            "release_expired_reservations failed (attempt %d): %s",
            self.request.retries + 1,
            exc,
        )
        raise self.retry(exc=exc)

    logger.info(
        "Released %d expired reservations across %d rooms",
        len(expired),
        len(room_increments),
    )
