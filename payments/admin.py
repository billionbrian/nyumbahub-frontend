from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'checkout_request_id',
        'phone_number',
        'amount',
        'status',
        'mpesa_receipt_number',
        'payment_type',
        'property',
        'created_at'
    )
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = (
        'checkout_request_id',
        'merchant_request_id',
        'phone_number',
        'mpesa_receipt_number',
        'property__title'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'raw_callback_payload'
    )
