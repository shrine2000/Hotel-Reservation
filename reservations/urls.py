from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView
from .views.hotel import HotelViewSet
from .views.room import RoomViewSet
from .views.reservations import ReservationViewSet
from .views.login_user import LoginView

router = DefaultRouter()
router.register(r"hotels", HotelViewSet, basename="hotel")
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"reservations", ReservationViewSet, basename="reservation")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
