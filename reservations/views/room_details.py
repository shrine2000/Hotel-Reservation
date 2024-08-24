from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reservations.models import Reservation
from reservations.serializers import ReservationSerializer
from rest_framework import serializers


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.validated_data["room"]
        if room.available_rooms < 1:
            raise serializers.ValidationError("No rooms available")
        serializer.save()
        room.available_rooms -= 1
        room.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
