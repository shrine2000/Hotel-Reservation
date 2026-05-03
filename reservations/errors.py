from dataclasses import dataclass


@dataclass(frozen=True)
class Error:
    code: str
    message: str

    def as_dict(self) -> dict:
        return {"code": self.code, "message": self.message}

    def with_message(self, message: str) -> "Error":
        return Error(self.code, message)

    def get_code(self) -> str:
        return self.code

    def get_message(self) -> str:
        return self.message


class Errors:
    INVALID_CREDENTIALS = Error("invalid_credentials", "Invalid username or password.")
    NO_ROOMS_AVAILABLE = Error(
        "no_rooms_available", "No rooms available for the selected room type."
    )
    INVALID_STATUS_TRANSITION = Error(
        "invalid_status_transition", "Invalid reservation status transition."
    )
    RESERVATION_NOT_CANCELLABLE = Error(
        "reservation_not_cancellable",
        "Reservation cannot be cancelled in its current status.",
    )
    GUEST_PROFILE_ALREADY_EXISTS = Error(
        "guest_profile_already_exists", "A guest profile already exists for this user."
    )
    PAYMENT_ALREADY_COMPLETED = Error(
        "payment_already_completed", "This payment has already been completed."
    )
    CHECK_IN_DATE_IN_PAST = Error(
        "check_in_date_in_past", "Check-in date cannot be in the past."
    )
    PERMISSION_DENIED = Error(
        "permission_denied", "You do not have permission to perform this action."
    )
    NOT_FOUND = Error("not_found", "The requested resource was not found.")
