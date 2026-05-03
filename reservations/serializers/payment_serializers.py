from decimal import Decimal

from rest_framework import serializers

from reservations.enums import PaymentMethod
from reservations.models.payment import Payment
from reservations.models.reservation import Reservation


class PaymentSerializer(serializers.ModelSerializer):
    reservation_uid = serializers.CharField(source="reservation.uid", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "uid",
            "reservation_uid",
            "amount",
            "payment_method",
            "status",
            "reference_id",
            "notes",
            "created_at",
        )
        read_only_fields = ("uid", "status", "created_at")


class PaymentCreateSerializer(serializers.Serializer):
    class Meta:
        model = Payment

    reservation_uid = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01")
    )
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices())
    reference_id = serializers.CharField(max_length=100, required=False, default="")
    notes = serializers.CharField(required=False, default="", allow_blank=True)

    def validate_reservation_uid(self, value) -> Reservation:
        try:
            return Reservation.objects.only(
                "uid", "user_id", "status", "total_cost", "is_active"
            ).get(uid=value, is_active=True)
        except Reservation.DoesNotExist:
            raise serializers.ValidationError("Reservation not found or inactive.")

    def validate_payment_method(self, value: str) -> str:
        if value not in PaymentMethod.values():
            raise serializers.ValidationError(
                f"Invalid payment method. Choices: {PaymentMethod.values()}"
            )
        return value
