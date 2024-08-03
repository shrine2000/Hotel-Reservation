from rest_framework import viewsets

from .models import Reservation
from .serializers import ReservationSerializer
from rest_framework import serializers


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def perform_create(self, serializer):
        room = serializer.validated_data["room"]
        if room.available_rooms < 1:
            raise serializers.ValidationError("No rooms available")
        serializer.save()
