import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentInitiateSerializer, PaymentSerializer
from .services.daraja import (
    MpesaDarajaClient,
    DarajaException,
    DarajaTimeoutException,
    DarajaConnectionException,
    DarajaAPIException,
)
from properties.models import Property

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def initiate_payment(request):
    """
    Initiate Lipa Na M-Pesa Online (STK Push) for property booking or rent.
    Accepts:
        - phone: Kenyan phone number (e.g., 0712345678, 254712345678)
        - amount: Numeric amount in KES
        - property_id (optional): ID of property being booked/paid
        - payment_type (optional): 'booking', 'rent', or 'deposit'
    """
    serializer = PaymentInitiateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Validation failed', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data
    phone = validated_data['phone']
    amount = validated_data['amount']
    property_id = validated_data.get('property_id')
    payment_type = validated_data.get('payment_type', Payment.TYPE_BOOKING)

    prop = None
    if property_id:
        try:
            prop = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            pass

    account_ref = f"PROP-{prop.id}" if prop else "NyumbaHub"
    trans_desc = f"Booking {prop.title[:15]}" if prop else "Rent Payment"

    daraja_client = MpesaDarajaClient()

    try:
        daraja_response = daraja_client.initiate_stk_push(
            phone_number=phone,
            amount=amount,
            account_reference=account_ref,
            transaction_desc=trans_desc
        )

        checkout_request_id = daraja_response.get('CheckoutRequestID')
        merchant_request_id = daraja_response.get('MerchantRequestID', '')

        # Create Payment record
        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            property=prop,
            merchant_request_id=merchant_request_id,
            checkout_request_id=checkout_request_id,
            phone_number=phone,
            amount=amount,
            payment_type=payment_type,
            status=Payment.STATUS_PENDING,
            raw_callback_payload={'initiate_response': daraja_response}
        )

        is_simulated = daraja_response.get('simulated', False)
        is_fallback = daraja_response.get('timeout_fallback', False) or daraja_response.get('network_fallback', False)

        if is_fallback:
            msg = 'Safaricom sandbox timed out; development fallback session initialized.'
        elif is_simulated:
            msg = 'Development Mode: Simulated M-Pesa STK Push initialized.'
        else:
            msg = 'M-Pesa payment prompt sent to your phone! Please enter your M-Pesa PIN.'

        return Response({
            'message': msg,
            'checkout_request_id': payment.checkout_request_id,
            'merchant_request_id': payment.merchant_request_id,
            'status': payment.status,
            'phone': payment.phone_number,
            'amount': str(payment.amount),
            'simulated': is_simulated
        }, status=status.HTTP_200_OK)

    except DarajaTimeoutException as e:
        logger.warning(f"Daraja STK push timeout: {e}")
        return Response(
            {
                'error': 'Safaricom M-Pesa is taking too long to respond. The sandbox server timed out. Please try again.',
                'code': 'GATEWAY_TIMEOUT',
                'details': str(e)
            },
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    except DarajaConnectionException as e:
        logger.warning(f"Daraja STK push connection error: {e}")
        return Response(
            {
                'error': 'Could not establish connection to Safaricom M-Pesa servers. Please check your internet connection.',
                'code': 'CONNECTION_ERROR',
                'details': str(e)
            },
            status=status.HTTP_502_BAD_GATEWAY
        )
    except (DarajaAPIException, ValueError) as e:
        logger.warning(f"Daraja STK push validation/API error: {e}")
        return Response(
            {
                'error': str(e),
                'code': 'DARAJA_ERROR'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.exception(f"Unexpected Daraja STK push error: {str(e)}")
        return Response(
            {
                'error': f"Failed to initiate M-Pesa STK push: {str(e)}",
                'code': 'SERVER_ERROR'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def mpesa_callback(request):
    """
    Safaricom Daraja Webhook Callback endpoint.
    Processes stkCallback from Safaricom servers.
    """
    payload = request.data
    logger.info(f"M-Pesa Daraja Callback received: {payload}")

    try:
        body = payload.get('Body', {})
        stk_callback = body.get('stkCallback', {})

        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc', '')

        if not checkout_request_id:
            logger.warning("Callback received without CheckoutRequestID")
            return Response({"ResultCode": 0, "ResultDesc": "Accepted with warning"})

        payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
        if not payment:
            logger.error(f"Payment record not found for CheckoutRequestID: {checkout_request_id}")
            return Response({"ResultCode": 0, "ResultDesc": "Accepted (Payment not found)"})

        if result_code == 0:
            # Extract CallbackMetadata
            metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            meta_dict = {item.get('Name'): item.get('Value') for item in metadata if 'Name' in item}

            receipt_number = meta_dict.get('MpesaReceiptNumber', '')
            trans_date_raw = str(meta_dict.get('TransactionDate', ''))

            # Parse YYYYMMDDHHmmss to datetime in Africa/Nairobi
            trans_date = None
            if trans_date_raw and len(trans_date_raw) == 14:
                try:
                    dt = datetime.strptime(trans_date_raw, '%Y%m%d%H%M%S')
                    trans_date = dt.replace(tzinfo=ZoneInfo('Africa/Nairobi'))
                except Exception as ex:
                    logger.warning(f"Could not parse transaction date: {trans_date_raw} ({ex})")

            payment.mark_completed(
                mpesa_receipt_number=receipt_number,
                transaction_date=trans_date,
                raw_payload=payload,
                result_desc=result_desc
            )
            logger.info(f"Payment {checkout_request_id} COMPLETED. Receipt: {receipt_number}")

        else:
            payment.mark_failed(
                result_code=result_code,
                result_desc=result_desc,
                raw_payload=payload
            )
            logger.info(f"Payment {checkout_request_id} FAILED ({result_code}): {result_desc}")

        # Safaricom expects a 200 OK with this JSON structure
        return Response({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Error handling M-Pesa callback: {str(e)}")
        return Response({
            "ResultCode": 0,
            "ResultDesc": "Error handled"
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def payment_status(request, checkout_request_id):
    """
    Check the current status of an STK Push transaction.
    Polled by the frontend to confirm when a payment completes, cancels, or times out.
    Features:
        1. Auto-confirm simulated sandbox transactions.
        2. Active Safaricom STK Push Query fallback with 5s throttling for real transactions
           where webhook callback cannot reach localhost.
    """
    payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
    if not payment:
        return Response(
            {'error': 'Payment transaction not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # If already resolved, return current state
    if payment.status != Payment.STATUS_PENDING:
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

    config = getattr(settings, 'MPESA_CONFIG', {})
    auto_confirm = config.get('AUTO_CONFIRM_SIMULATION', True)
    initiate_resp = payment.raw_callback_payload.get('initiate_response', {}) if payment.raw_callback_payload else {}
    is_simulated = initiate_resp.get('simulated', False)

    # 1. Simulated payment auto-completion in development
    if is_simulated and auto_confirm:
        elapsed = (timezone.now() - payment.created_at).total_seconds()
        if elapsed >= 3:
            payment.mark_completed(
                mpesa_receipt_number=f"SIM{payment.id}{payment.created_at.strftime('%H%M%S')}",
                transaction_date=timezone.now(),
                result_desc="Development simulated payment confirmation"
            )
            logger.info(f"Auto-confirmed simulated sandbox payment {checkout_request_id}")
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

    # 2. Real STK Push active query fallback (essential for localhost development where Safaricom webhooks cannot reach laptop)
    if not is_simulated:
        elapsed = (timezone.now() - payment.created_at).total_seconds()
        # Wait at least 3 seconds from creation before first query to let user receive prompt
        if elapsed >= 3:
            throttle_key = f"stk_query_throttle_{checkout_request_id}"
            # Only query Safaricom once every 5 seconds to avoid SpikeArrestViolation (rate limit)
            if not cache.get(throttle_key):
                cache.set(throttle_key, True, timeout=5)
                try:
                    daraja_client = MpesaDarajaClient()
                    query_res = daraja_client.query_stk_status(checkout_request_id)
                    res_code = str(query_res.get('ResultCode', ''))
                    res_desc = query_res.get('ResultDesc', '') or query_res.get('ResponseDescription', '')

                    if res_code == '0':
                        payment.mark_completed(
                            mpesa_receipt_number=query_res.get('MpesaReceiptNumber') or f"QGH{payment.id}{payment.created_at.strftime('%H%M')}",
                            transaction_date=timezone.now(),
                            raw_payload=query_res,
                            result_desc=res_desc or "Transaction completed successfully"
                        )
                        logger.info(f"Payment {checkout_request_id} confirmed via STK Query.")
                    elif res_code == '1032':
                        payment.mark_failed(
                            result_code=1032,
                            result_desc=res_desc or "Request Cancelled by user.",
                            raw_payload=query_res
                        )
                        logger.info(f"Payment {checkout_request_id} cancelled by user via STK Query.")
                    elif res_code == '1037':
                        payment.mark_failed(
                            result_code=1037,
                            result_desc=res_desc or "DS timeout / No response from user.",
                            raw_payload=query_res
                        )
                        logger.info(f"Payment {checkout_request_id} timed out via STK Query.")
                    elif res_code and res_code not in ('', 'None'):
                        if 'being processed' not in res_desc.lower() and 'fault' not in str(query_res).lower():
                            try:
                                code_int = int(res_code)
                            except (ValueError, TypeError):
                                code_int = -1
                            payment.mark_failed(
                                result_code=code_int,
                                result_desc=res_desc,
                                raw_payload=query_res
                            )
                            logger.info(f"Payment {checkout_request_id} failed ({code_int}) via STK Query: {res_desc}")
                except Exception as e:
                    logger.warning(f"STK query failed for {checkout_request_id}: {e}")

    return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def simulate_callback(request):
    """
    Development testing utility: Simulates a successful or failed Daraja callback
    for local testing without needing ngrok/public tunnel.
    """
    checkout_request_id = request.data.get('checkout_request_id')
    result_code = request.data.get('result_code', 0)
    receipt_no = request.data.get('receipt_no', 'SIM' + datetime.now().strftime('%H%M%S'))

    if not checkout_request_id:
        return Response({'error': 'checkout_request_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
    if not payment:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

    if result_code == 0:
        payment.mark_completed(
            mpesa_receipt_number=receipt_no,
            transaction_date=datetime.now(ZoneInfo('Africa/Nairobi')),
            result_desc="Development simulated payment confirmation"
        )
    else:
        payment.mark_failed(
            result_code=result_code,
            result_desc="Development simulated payment failure"
        )

    return Response({
        'message': f'Simulated status updated to {payment.status}',
        'payment': PaymentSerializer(payment).data
    })
