#!/bin/bash

# Activate the virtual environment and start Celery worker
poetry run celery -A hotel_reservation worker --loglevel=info
