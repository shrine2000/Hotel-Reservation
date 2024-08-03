#!/bin/bash

poetry run celery -A hotel_reservation beat --loglevel=info
