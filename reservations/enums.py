from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(tag.value, tag.name.replace("_", " ").capitalize()) for tag in cls]

    @classmethod
    def values(cls) -> list[str]:
        return [tag.value for tag in cls]


class RoomType(BaseEnum):
    SINGLE = "S"
    DOUBLE = "D"
    SUITE = "SU"


class RoomLuxury(BaseEnum):
    DELUXE = "D"
    SUPER_DELUXE = "SD"


class ReservationStatus(BaseEnum):
    PENDING = "PE"
    CONFIRMED = "CO"
    CHECKED_IN = "CI"
    CHECKED_OUT = "CH"
    CANCELLED = "CA"


class PaymentMethod(BaseEnum):
    CASH = "CA"
    CREDIT_CARD = "CC"
    ONLINE = "ON"


class PaymentStatus(BaseEnum):
    PENDING = "PE"
    COMPLETED = "CO"
    FAILED = "FA"
    REFUNDED = "RE"
