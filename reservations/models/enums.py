from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def choices(cls):
        return [(tag.value, tag.name.replace("_", " ").capitalize()) for tag in cls]

    @classmethod
    def names(cls):
        return [tag.name.capitalize() for tag in cls]


class RoomType(BaseEnum):
    SINGLE = "S"
    DOUBLE = "D"


class RoomLuxury(BaseEnum):
    DELUXE = "D"
    SUPER_DELUXE = "SD"
