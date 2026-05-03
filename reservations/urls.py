from django.urls import include, path
from rest_framework.routers import DefaultRouter

from reservations.views import RegisterView
from reservations.views.auth import ChangePasswordView, LogoutView, ProfileView
from reservations.views.guest import GuestProfileViewSet
from reservations.views.hotel import HotelViewSet
from reservations.views.hotel_photo import HotelPhotoViewSet
from reservations.views.login_user import LoginView
from reservations.views.payment import PaymentViewSet
from reservations.views.reservations import ReservationViewSet
from reservations.views.review import HotelReviewViewSet
from reservations.views.room import RoomViewSet

router = DefaultRouter()
router.register(r"hotels", HotelViewSet, basename="hotel")
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"reservations", ReservationViewSet, basename="reservation")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"guests", GuestProfileViewSet, basename="guest")
router.register(r"reviews", HotelReviewViewSet, basename="review")
router.register(r"hotel-photos", HotelPhotoViewSet, basename="hotel-photo")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
