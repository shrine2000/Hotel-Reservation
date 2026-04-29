import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse

from hotel_reservation.context import get_request_id, set_request_id


class RequestIDMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        set_request_id(request_id)
        response = self.get_response(request)
        response["X-Request-Id"] = get_request_id()
        return response
