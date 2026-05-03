from rest_framework import status
from rest_framework.exceptions import APIException

from reservations.errors import Error, Errors


class HotelException(APIException):
    """Business conflict — 409."""

    status_code = status.HTTP_409_CONFLICT
    _default_error: Error = Error("hotel_error", "A conflict occurred.")

    def __init__(self, error: Error | None = None) -> None:
        err = error or self._default_error
        self.error = err
        super().__init__(detail=err.get_message(), code=err.get_code())


class HotelPermissionException(APIException):
    """Permission denied — 403."""

    status_code = status.HTTP_403_FORBIDDEN
    _default_error: Error = Errors.PERMISSION_DENIED

    def __init__(self, error: Error | None = None) -> None:
        err = error or self._default_error
        self.error = err
        super().__init__(detail=err.get_message(), code=err.get_code())


class HotelBusinessException(APIException):
    """Bad request — 400."""

    status_code = status.HTTP_400_BAD_REQUEST
    _default_error: Error = Error("bad_request", "Invalid request.")

    def __init__(self, error: Error | None = None) -> None:
        err = error or self._default_error
        self.error = err
        super().__init__(detail=err.get_message(), code=err.get_code())


class NotFound404(APIException):
    """Not found — 404."""

    status_code = status.HTTP_404_NOT_FOUND
    _default_error: Error = Errors.NOT_FOUND

    def __init__(self, error: Error | None = None) -> None:
        err = error or self._default_error
        self.error = err
        super().__init__(detail=err.get_message(), code=err.get_code())


class InvalidCredentialsError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    _default_error: Error = Errors.INVALID_CREDENTIALS

    def __init__(self, error: Error | None = None) -> None:
        err = error or self._default_error
        self.error = err
        super().__init__(detail=err.get_message(), code=err.get_code())


class NoRoomsAvailableError(HotelException):
    _default_error = Errors.NO_ROOMS_AVAILABLE


class InvalidReservationStatusTransitionError(HotelException):
    _default_error = Errors.INVALID_STATUS_TRANSITION


class ReservationNotCancellableError(HotelException):
    _default_error = Errors.RESERVATION_NOT_CANCELLABLE


class GuestProfileAlreadyExistsError(HotelException):
    _default_error = Errors.GUEST_PROFILE_ALREADY_EXISTS


class PaymentAlreadyCompletedError(HotelException):
    _default_error = Errors.PAYMENT_ALREADY_COMPLETED


class CheckInDateInPastError(HotelBusinessException):
    _default_error = Errors.CHECK_IN_DATE_IN_PAST
