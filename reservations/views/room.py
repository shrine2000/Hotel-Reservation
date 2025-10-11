import logging
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from reservations.models.room import Room
from reservations.serializers import RoomSerializer
from reservations.filters import RoomFilter

logger = logging.getLogger(__name__)


class RoomViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    serializer_class = RoomSerializer
    queryset = (
        Room.objects.filter(is_active=True)
        .select_related("hotel")
        .order_by("-created_at")
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ["hotel__name", "hotel__location"]
    search_param = "search"
    filterset_class = RoomFilter
    lookup_field = "uid"
    http_method_names = ["get", "post", "patch"]
