from rest_framework import serializers
from decimal import Decimal

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    can_be_refunded = serializers.BooleanField(read_only=True)
    remaining_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = [
            'id',
            'stripe_payment_intent_id',
            'stripe_charge_id',
            'status',
            'refund_amount',
            'created_at',
            'updated_at'
        ]


class CreatePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.50'),
        help_text='Сума в основній валюті'
    )
    currency = serializers.ChoiceField(
        choices=['usd', 'uah', 'eur'],
        default='usd',
        help_text='Код валюти'
    )
    description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text='Опис платежу'
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict,
        help_text='Додаткові дані'
    )
