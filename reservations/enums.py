from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(tag.value, tag.name.replace("_", " ").capitalize()) for tag in cls]

    @classmethod
    def names(cls) -> list[str]:
        return [tag.name.capitalize() for tag in cls]


class RoomType(BaseEnum):
    SINGLE = "S"
    DOUBLE = "D"


class RoomLuxury(BaseEnum):
    DELUXE = "D"
    SUPER_DELUXE = "SD"
