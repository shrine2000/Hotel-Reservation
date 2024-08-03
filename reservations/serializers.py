from rest_framework import serializers
from .models import Hotel, Room, Reservation
from django.contrib.auth.models import User


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class ReservationSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Reservation
        fields = "__all__"

    def validate(self, data):
        room = data.get("room")
        if room.available_rooms < 1:
            raise serializers.ValidationError("No rooms available")
        return data
