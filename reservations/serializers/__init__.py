from reservations.serializers.auth_serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    UserRegisterSerializer,
)
from reservations.serializers.guest_serializers import (
    GuestProfileCreateSerializer,
    GuestProfileSerializer,
    GuestProfileUpdateSerializer,
)
from reservations.serializers.hotel_photo_serializers import (
    HotelPhotoCreateSerializer,
    HotelPhotoSerializer,
)
from reservations.serializers.hotel_serializers import (
    HotelCreateSerializer,
    HotelDetailSerializer,
    HotelSerializer,
    HotelUpdateSerializer,
)
from reservations.serializers.payment_serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
)
from reservations.serializers.reservation_serializers import (
    ReservationCreateSerializer,
    ReservationModifySerializer,
    ReservationSerializer,
)
from reservations.serializers.review_serializers import (
    HotelReviewCreateSerializer,
    HotelReviewSerializer,
    HotelReviewUpdateSerializer,
)
from reservations.serializers.room_serializers import (
    RoomCreateSerializer,
    RoomSerializer,
    RoomUpdateSerializer,
)

UserSerializer = UserRegisterSerializer

__all__ = [
    "LoginSerializer",
    "UserSerializer",
    "UserRegisterSerializer",
    "ProfileSerializer",
    "ProfileUpdateSerializer",
    "ChangePasswordSerializer",
    "HotelSerializer",
    "HotelDetailSerializer",
    "HotelCreateSerializer",
    "HotelUpdateSerializer",
    "RoomSerializer",
    "RoomCreateSerializer",
    "RoomUpdateSerializer",
    "ReservationSerializer",
    "ReservationCreateSerializer",
    "ReservationModifySerializer",
    "PaymentSerializer",
    "PaymentCreateSerializer",
    "GuestProfileSerializer",
    "GuestProfileCreateSerializer",
    "GuestProfileUpdateSerializer",
    "HotelPhotoSerializer",
    "HotelPhotoCreateSerializer",
    "HotelReviewSerializer",
    "HotelReviewCreateSerializer",
    "HotelReviewUpdateSerializer",
]
