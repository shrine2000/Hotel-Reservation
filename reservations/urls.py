from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView
from .views.hotel import (
    HotelListView,
    HotelDetailView,
    HotelCreateView,
    HotelUpdateView,
    HotelDeactivateView,
)
from .views.login_user import LoginView

router = DefaultRouter()
urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("hotels/", HotelListView.as_view(), name="hotel-list"),
    path("hotels/<int:pk>/", HotelDetailView.as_view(), name="hotel-detail"),
    path("hotels/add/", HotelCreateView.as_view(), name="hotel-create"),
    path("hotels/<int:pk>/edit/", HotelUpdateView.as_view(), name="hotel-update"),
    path(
        "hotels/<int:pk>/deactivate/",
        HotelDeactivateView.as_view(),
        name="hotel-deactivate",
    ),
]
