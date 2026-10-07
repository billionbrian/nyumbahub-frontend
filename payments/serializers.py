from rest_framework import serializers
from .models import Payment
from .services.daraja import format_phone_number
from properties.models import Property


class PaymentInitiateSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1, required=True)
    property_id = serializers.IntegerField(required=False, allow_null=True)
    payment_type = serializers.ChoiceField(
        choices=Payment.PAYMENT_TYPE_CHOICES,
        default=Payment.TYPE_BOOKING,
        required=False
    )

    def validate_phone(self, value):
        try:
            return format_phone_number(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def validate_property_id(self, value):
        if value:
            if not Property.objects.filter(id=value).exists():
                raise serializers.ValidationError("Property does not exist.")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_location = serializers.CharField(source='property.location', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'checkout_request_id',
            'merchant_request_id',
            'phone_number',
            'amount',
            'payment_type',
            'status',
            'mpesa_receipt_number',
            'transaction_date',
            'result_code',
            'result_desc',
            'property',
            'property_title',
            'property_location',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
