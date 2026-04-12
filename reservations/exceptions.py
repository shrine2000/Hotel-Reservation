from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidCredentialsError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid username or password"
    default_code = "invalid_credentials"


class NoRoomsAvailableError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "No rooms available"
    default_code = "no_rooms_available"
