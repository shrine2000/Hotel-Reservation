from django.conf import settings
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AuthUserThrottle(UserRateThrottle):
    scope = "auth_user"

    def allow_request(self, request, view):
        if settings.TESTING:
            return True
        return super().allow_request(request, view)


class AuthAnonThrottle(AnonRateThrottle):
    scope = "auth_anon"

    def allow_request(self, request, view):
        if settings.TESTING:
            return True
        return super().allow_request(request, view)


class PaymentThrottle(UserRateThrottle):
    scope = "payment"
