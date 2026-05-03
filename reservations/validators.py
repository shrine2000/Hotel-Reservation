import html
from enum import Enum

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible


class ValidationPattern(str, Enum):
    """Whitelisted character patterns for input validation. Using a whitelist
    implicitly blocks XSS vectors (<, >, script) and SQL injection characters."""

    ALPHANUMERIC = r"^[a-zA-Z0-9]+$"
    ALPHANUMERIC_WITH_DASH = r"^[a-zA-Z0-9\-]+$"
    ALPHABETIC_ONLY = r"^[a-zA-Z\s]+$"
    NUMERIC_ONLY = r"^[0-9]+$"

    PERSON_NAME = r"^[a-zA-Z\s\.\-']+$"
    COMPANY_NAME = r"^[a-zA-Z0-9\s\.\-&'(),/]+$"
    ADDRESS = r"^[a-zA-Z0-9\s\.\-,#/()&']+$"

    SAFE_TEXT = r"^[0-9a-zA-ZÀ-ſ\s.,'\-/&_():;!@#$%*+= \[\]{}|~]+$"

    REFERENCE_ID = r"^[A-Za-z0-9\-_]+$"


@deconstructible
class CharacterPatternValidator(RegexValidator):
    """
    Validates that a field contains only characters from a named whitelist pattern.
    HTML-unescapes the value before checking so encoded payloads are caught.
    Skips validation for empty / blank values.

    Usage:
        name = models.CharField(validators=[CharacterPatternValidator("COMPANY_NAME")])
    """

    def __init__(self, regex_pattern: str = "SAFE_TEXT", message: str = ""):
        if regex_pattern not in ValidationPattern.__members__:
            raise ValueError(f"Unknown validation pattern: '{regex_pattern}'")
        self.regex_pattern = regex_pattern
        regex = ValidationPattern[regex_pattern].value
        super().__init__(
            regex,
            message=message or f"Invalid characters. Allowed pattern: {regex_pattern}.",
        )

    def __call__(self, value: str) -> None:
        if not value or not value.strip():
            return
        unescaped = html.unescape(value)
        try:
            super().__call__(unescaped)
        except ValidationError as exc:
            raise ValidationError(
                "Invalid input: contains disallowed characters."
            ) from exc

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CharacterPatternValidator)
            and self.regex_pattern == other.regex_pattern
            and self.message == other.message
        )

    def deconstruct(self):
        path = f"{self.__module__}.{self.__class__.__name__}"
        return path, [self.regex_pattern], {"message": self.message}


def validate_not_blank(value: str) -> None:
    """Reject strings that are non-empty but contain only whitespace."""
    if value and not value.strip():
        raise ValidationError("This field cannot contain only whitespace.")
