from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from reservations.models.models import Reservation
from reservations.serializers import ReservationSerializer
from rest_framework import serializers


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        room = serializer.validated_data["room"]
        if room.available_rooms < 1:
            raise serializers.ValidationError("No rooms available")
        serializer.save()
