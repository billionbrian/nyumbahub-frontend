from django.db import models
from django.conf import settings


class Payment(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    TYPE_BOOKING = 'booking'
    TYPE_RENT = 'rent'
    TYPE_DEPOSIT = 'deposit'

    PAYMENT_TYPE_CHOICES = [
        (TYPE_BOOKING, 'Property Booking'),
        (TYPE_RENT, 'Rent Payment'),
        (TYPE_DEPOSIT, 'Security Deposit'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )

    # Daraja Identifiers
    merchant_request_id = models.CharField(max_length=100, db_index=True)
    checkout_request_id = models.CharField(max_length=100, unique=True, db_index=True)

    # Financial details
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        default=TYPE_BOOKING
    )

    # Status & Callback Metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(blank=True, default='')
    raw_callback_payload = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"Payment {self.checkout_request_id} - KES {self.amount} ({self.status})"

    def is_successful(self):
        return self.status == self.STATUS_COMPLETED

    def mark_completed(self, mpesa_receipt_number, transaction_date=None, raw_payload=None, result_desc=''):
        self.status = self.STATUS_COMPLETED
        self.mpesa_receipt_number = mpesa_receipt_number
        self.result_code = 0
        if transaction_date:
            self.transaction_date = transaction_date
        if result_desc:
            self.result_desc = result_desc
        if raw_payload:
            self.raw_callback_payload = raw_payload
        self.save()

        # If booking fee, update property status to 'booked'
        if self.property and self.payment_type == self.TYPE_BOOKING:
            self.property.status = 'booked'
            self.property.available = False
            self.property.save(update_fields=['status', 'available'])

    def mark_failed(self, result_code, result_desc='', raw_payload=None):
        if result_code == 1032:
            self.status = self.STATUS_CANCELLED
        else:
            self.status = self.STATUS_FAILED

        self.result_code = result_code
        self.result_desc = result_desc
        if raw_payload:
            self.raw_callback_payload = raw_payload
        self.save()
