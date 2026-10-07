from datetime import timedelta
from unittest.mock import patch
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from properties.models import Property
from accounts.models import User
from payments.models import Payment
from payments.services.daraja import (
    format_phone_number,
    MpesaDarajaClient,
    DarajaTimeoutException,
    DarajaConnectionException,
)


class MpesaDarajaTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testtenant',
            email='tenant@example.com',
            password='password123',
            role='tenant'
        )
        self.landlord = User.objects.create_user(
            username='testlandlord',
            email='landlord@example.com',
            password='password123',
            role='landlord'
        )
        self.property = Property.objects.create(
            landlord=self.landlord,
            title='Sunset Studio Nairobi',
            description='Cozy modern bedsitter',
            location='Madaraka, Nairobi',
            rent_amount=15000.00,
            property_type='bedsitter',
            status='available'
        )

    def test_phone_number_formatting(self):
        self.assertEqual(format_phone_number('0712345678'), '254712345678')
        self.assertEqual(format_phone_number('+254712345678'), '254712345678')
        self.assertEqual(format_phone_number('254712345678'), '254712345678')
        self.assertEqual(format_phone_number('0112345678'), '254112345678')
        self.assertEqual(format_phone_number('712345678'), '254712345678')

        with self.assertRaises(ValueError):
            format_phone_number('12345')

        with self.assertRaises(ValueError):
            format_phone_number('0612345678')

    @patch('payments.views.MpesaDarajaClient.initiate_stk_push')
    def test_initiate_payment_api(self, mock_stk):
        mock_stk.return_value = {
            'MerchantRequestID': 'MR-TEST-999',
            'CheckoutRequestID': 'ws_CO_TEST_MOCK_001',
            'ResponseCode': '0',
            'ResponseDescription': 'Success. Request accepted for processing',
            'CustomerMessage': 'Success. Request accepted for processing'
        }
        url = '/api/payments/initiate/'
        payload = {
            'phone': '0712345678',
            'amount': 1500,
            'property_id': self.property.id,
            'payment_type': 'booking'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['checkout_request_id'], 'ws_CO_TEST_MOCK_001')
        self.assertEqual(data['phone'], '254712345678')
        self.assertEqual(data['status'], 'PENDING')

        payment = Payment.objects.get(checkout_request_id='ws_CO_TEST_MOCK_001')
        self.assertEqual(payment.property, self.property)
        self.assertEqual(float(payment.amount), 1500.00)

    def test_daraja_callback_success(self):
        # Create pending payment
        payment = Payment.objects.create(
            property=self.property,
            merchant_request_id='MR12345',
            checkout_request_id='ws_CO_TEST_001',
            phone_number='254712345678',
            amount=1500.00,
            payment_type='booking',
            status='PENDING'
        )

        callback_payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "MR12345",
                    "CheckoutRequestID": "ws_CO_TEST_001",
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 1500.00},
                            {"Name": "MpesaReceiptNumber", "Value": "QGH789XYZ"},
                            {"Name": "TransactionDate", "Value": 20261005123000},
                            {"Name": "PhoneNumber", "Value": 254712345678}
                        ]
                    }
                }
            }
        }

        response = self.client.post('/api/payments/callback/', callback_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(payment.mpesa_receipt_number, 'QGH789XYZ')
        self.assertEqual(payment.result_code, 0)

        # Property should now be booked!
        self.property.refresh_from_db()
        self.assertEqual(self.property.status, 'booked')
        self.assertFalse(self.property.available)

    def test_daraja_callback_user_cancelled(self):
        payment = Payment.objects.create(
            property=self.property,
            merchant_request_id='MR12346',
            checkout_request_id='ws_CO_TEST_002',
            phone_number='254712345678',
            amount=1500.00,
            status='PENDING'
        )

        callback_payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "MR12346",
                    "CheckoutRequestID": "ws_CO_TEST_002",
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user"
                }
            }
        }

        response = self.client.post('/api/payments/callback/', callback_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'CANCELLED')
        self.assertEqual(payment.result_code, 1032)

    def test_payment_status_endpoint(self):
        payment = Payment.objects.create(
            property=self.property,
            merchant_request_id='MR12347',
            checkout_request_id='ws_CO_TEST_003',
            phone_number='254712345678',
            amount=1500.00,
            status='PENDING'
        )

        response = self.client.get(f'/api/payments/status/{payment.checkout_request_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['checkout_request_id'], payment.checkout_request_id)
        self.assertEqual(data['status'], 'PENDING')

    @patch('payments.views.MpesaDarajaClient.initiate_stk_push')
    def test_initiate_payment_timeout_returns_504(self, mock_stk):
        mock_stk.side_effect = DarajaTimeoutException("Safaricom sandbox timed out after 30s")
        url = '/api/payments/initiate/'
        payload = {
            'phone': '0712345678',
            'amount': 1500,
            'property_id': self.property.id,
            'payment_type': 'booking'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        data = response.json()
        self.assertEqual(data['code'], 'GATEWAY_TIMEOUT')
        self.assertIn('timed out', data['error'])

    @patch('payments.views.MpesaDarajaClient.initiate_stk_push')
    def test_initiate_payment_connection_error_returns_502(self, mock_stk):
        mock_stk.side_effect = DarajaConnectionException("Could not connect to Safaricom")
        url = '/api/payments/initiate/'
        payload = {
            'phone': '0712345678',
            'amount': 1500,
            'property_id': self.property.id,
            'payment_type': 'booking'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        data = response.json()
        self.assertEqual(data['code'], 'CONNECTION_ERROR')

    @patch('payments.views.MpesaDarajaClient.query_stk_status')
    def test_payment_status_reflects_user_cancelled_via_stk_query(self, mock_query):
        mock_query.return_value = {
            'ResponseCode': '0',
            'ResultCode': '1032',
            'ResultDesc': 'Request Cancelled by user.'
        }
        payment = Payment.objects.create(
            property=self.property,
            merchant_request_id='MR12348',
            checkout_request_id='ws_CO_TEST_004',
            phone_number='254712345678',
            amount=1500.00,
            status='PENDING',
            raw_callback_payload={'initiate_response': {'simulated': False}}
        )
        Payment.objects.filter(id=payment.id).update(created_at=timezone.now() - timedelta(seconds=10))

        response = self.client.get(f'/api/payments/status/{payment.checkout_request_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'CANCELLED')
        self.assertEqual(data['result_code'], 1032)

    @patch('payments.views.MpesaDarajaClient.query_stk_status')
    def test_payment_status_reflects_timeout_via_stk_query(self, mock_query):
        mock_query.return_value = {
            'ResponseCode': '0',
            'ResultCode': '1037',
            'ResultDesc': 'No response from user.'
        }
        payment = Payment.objects.create(
            property=self.property,
            merchant_request_id='MR12349',
            checkout_request_id='ws_CO_TEST_005',
            phone_number='254712345678',
            amount=1500.00,
            status='PENDING',
            raw_callback_payload={'initiate_response': {'simulated': False}}
        )
        Payment.objects.filter(id=payment.id).update(created_at=timezone.now() - timedelta(seconds=10))

        response = self.client.get(f'/api/payments/status/{payment.checkout_request_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'FAILED')
        self.assertEqual(data['result_code'], 1037)

