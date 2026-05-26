from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AuthUserThrottle(UserRateThrottle):
    scope = "auth_user"


class AuthAnonThrottle(AnonRateThrottle):
    scope = "auth_anon"


class PaymentThrottle(UserRateThrottle):
    scope = "payment"
