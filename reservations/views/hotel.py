import logging
from rest_framework import viewsets, filters
from dry_rest_permissions.generics import DRYPermissions
from reservations.models.hotel import Hotel
from reservations.serializers import HotelSerializer

logger = logging.getLogger(__name__)


class HotelViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    serializer_class = HotelSerializer
    queryset = Hotel.objects.filter(is_active=True).order_by("-created_at")
    filter_backends = (filters.SearchFilter,)
    search_fields = ["name", "location"]
    search_param = "search"
    lookup_field = "uid"
    http_method_names = ["get", "post", "patch"]
