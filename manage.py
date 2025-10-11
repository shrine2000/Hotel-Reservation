#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def is_command_allowed(command):
    allowed_commands = {
        "runserver",
        "migrate",
        "makemigrations",
        "collectstatic",
        "shell",
        "sqlmigrate",
        "check",
        "shell_plus",
    }
    if command in allowed_commands:
        return True

    for allowed_cmd in allowed_commands:
        if command.startswith(allowed_cmd):
            return True
    return False


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_reservation.settings")

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if not is_command_allowed(command=command):
            print("Invalid Command")
            sys.exit(1)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
