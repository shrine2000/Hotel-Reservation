from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_reservation.settings")

app = Celery("hotel_reservation")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "release-expired-reservations": {
        "task": "reservations.tasks.release_expired_reservations",
        "schedule": timedelta(hours=24),
    },
}
