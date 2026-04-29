import logging
from collections import defaultdict
from datetime import date, timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import DateField, DurationField, ExpressionWrapper, F

from reservations.models import Reservation, Room

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300, ignore_result=True)
def release_expired_reservations(self) -> None:
    today = date.today()

    # Step 1: turn the integer field into a duration  (e.g. 3  →  3 days)
    stay_duration = ExpressionWrapper(
        F("number_of_days") * timedelta(days=1),
        output_field=DurationField(),
    )
    # Step 2: add that duration to check_in_date to get the checkout date
    checkout_date = ExpressionWrapper(
        F("check_in_date") + stay_duration,
        output_field=DateField(),
    )
    expired = list(
        Reservation.objects.filter(is_active=True)
        .annotate(checkout_date=checkout_date)
        .filter(checkout_date__lte=today)
        .select_related("room")
    )

    if not expired:
        logger.info("No expired reservations to release")
        return

    room_increments: dict[int, int] = defaultdict(int)
    for reservation in expired:
        room_increments[reservation.room.id] += 1

    expired_ids = [r.id for r in expired]

    try:
        with transaction.atomic():
            for room_id, increment in room_increments.items():
                Room.objects.filter(id=room_id).update(
                    available_rooms=F("available_rooms") + increment
                )
            Reservation.objects.filter(id__in=expired_ids).update(is_active=False)
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
