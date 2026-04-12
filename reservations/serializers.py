from typing import Any

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from reservations.models import Room, Hotel, Reservation
from reservations.exceptions import InvalidCredentialsError


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

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        room = attrs.get("room")
        if room.available_rooms < 1:
            raise serializers.ValidationError("No rooms available")
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "email")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: dict[str, Any]) -> User:
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise InvalidCredentialsError()
        attrs["user"] = user
        return attrs
