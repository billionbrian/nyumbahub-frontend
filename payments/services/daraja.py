import base64
import logging
import re
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Process-level in-memory token cache fallback
_MEMORY_TOKEN_CACHE = {}


class DarajaException(Exception):
    """Base exception for all Daraja operations."""
    pass


class DarajaTimeoutException(DarajaException):
    """Raised when request to Safaricom Daraja API times out."""
    pass


class DarajaConnectionException(DarajaException):
    """Raised when connection to Safaricom Daraja API fails."""
    pass


class DarajaAPIException(DarajaException):
    """Raised when Daraja returns an error response."""
    def __init__(self, message: str, status_code: int = None, raw_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.raw_data = raw_data or {}


def format_phone_number(phone: str) -> str:
    """
    Format and validate Kenyan phone number to 254XXXXXXXXX.
    Accepts:
        0712345678 -> 254712345678
        0112345678 -> 254112345678
        +254712345678 -> 254712345678
        254712345678 -> 254712345678
        712345678 -> 254712345678
    """
    if not phone:
        raise ValueError("Phone number is required")

    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', str(phone).strip())

    if cleaned.startswith('0') and len(cleaned) == 10:
        cleaned = '254' + cleaned[1:]
    elif (cleaned.startswith('7') or cleaned.startswith('1')) and len(cleaned) == 9:
        cleaned = '254' + cleaned
    elif cleaned.startswith('254') and len(cleaned) == 12:
        pass
    else:
        raise ValueError(
            f"Invalid Kenyan phone number '{phone}'. Expected 10 digits (e.g., 0712345678 or 0112345678)"
        )

    # Validate Kenyan prefix (2547... or 2541...)
    if not re.match(r'^254(7\d{8}|1\d{8})$', cleaned):
        raise ValueError(
            f"Invalid phone number '{phone}'. Must be a valid Safaricom/Airtel number starting with 07 or 01"
        )

    return cleaned


class MpesaDarajaClient:
    """
    Client for interacting with Safaricom Daraja API (STK Push & Query).
    Features:
        - Resilient HTTP connection pool with automatic retries on transient network errors.
        - Multi-tier OAuth caching (Django Cache + In-Memory process fallback).
        - Configurable connection and read timeouts.
        - Graceful sandbox simulation fallback when Safaricom Sandbox has high latency or downtime.
    """

    def __init__(self):
        config = getattr(settings, 'MPESA_CONFIG', {})
        self.environment = config.get('ENVIRONMENT', 'sandbox')
        self.consumer_key = config.get('CONSUMER_KEY', '').strip()
        self.consumer_secret = config.get('CONSUMER_SECRET', '').strip()
        self.shortcode = str(config.get('SHORTCODE', '174379')).strip()
        self.passkey = config.get(
            'PASSKEY',
            'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        ).strip()
        self.callback_url = config.get('CALLBACK_URL', 'https://sandbox.safaricom.co.ke/mpesa/').strip()
        self.timeout = int(config.get('TIMEOUT', 30))
        self.fallback_on_timeout = bool(config.get('FALLBACK_ON_TIMEOUT', True))

        if self.environment == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'

        # Configure resilient session with HTTPAdapter and retries
        self.session = requests.Session()
        retries = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def is_configured(self) -> bool:
        """Check if Daraja consumer credentials are provided."""
        return bool(self.consumer_key and self.consumer_secret)

    def get_access_token(self) -> str:
        """
        Fetch or retrieve cached OAuth access token from Safaricom Daraja.
        Uses Django Cache with an in-memory process cache fallback.
        """
        cache_key = f'mpesa_access_token_{self.environment}'
        cached_token = cache.get(cache_key)
        if cached_token:
            return cached_token

        # Check in-memory process cache
        mem_cached = _MEMORY_TOKEN_CACHE.get(self.environment)
        if mem_cached and time.time() < mem_cached.get('expires_at', 0):
            return mem_cached['token']

        if not self.is_configured():
            if self.environment == 'sandbox':
                return "simulated_sandbox_token"
            raise ValueError(
                "M-Pesa Consumer Key and Consumer Secret are not configured in .env."
            )

        token_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"

        try:
            response = self.session.get(
                token_url,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=(10, self.timeout)
            )
        except requests.exceptions.Timeout as e:
            logger.warning(f"Safaricom OAuth token request timed out after {self.timeout}s: {e}")
            if self.environment == 'sandbox' and self.fallback_on_timeout:
                logger.info("Sandbox fallback: Using mock token due to OAuth timeout.")
                return "simulated_sandbox_token"
            raise DarajaTimeoutException(
                f"Safaricom Daraja OAuth server timed out after {self.timeout} seconds."
            ) from e
        except requests.exceptions.RequestException as e:
            logger.warning(f"Safaricom OAuth connection error: {e}")
            if self.environment == 'sandbox' and self.fallback_on_timeout:
                logger.info("Sandbox fallback: Using mock token due to connection error.")
                return "simulated_sandbox_token"
            raise DarajaConnectionException("Could not connect to Safaricom Daraja OAuth server.") from e

        if response.status_code != 200:
            logger.error(f"Failed to fetch Daraja OAuth token: {response.status_code} - {response.text}")
            if self.environment == 'sandbox' and self.fallback_on_timeout:
                return "simulated_sandbox_token"
            raise DarajaAPIException(
                f"Daraja OAuth authentication failed: {response.text}",
                status_code=response.status_code
            )

        try:
            data = response.json()
        except Exception:
            if self.environment == 'sandbox' and self.fallback_on_timeout:
                return "simulated_sandbox_token"
            raise DarajaAPIException("Invalid JSON received from Daraja OAuth endpoint.")

        access_token = data.get('access_token')
        if not access_token:
            if self.environment == 'sandbox' and self.fallback_on_timeout:
                return "simulated_sandbox_token"
            raise DarajaAPIException("No access_token returned by Daraja OAuth endpoint.")

        expires_in = int(data.get('expires_in', 3599))
        cache_ttl = max(60, expires_in - 120)

        # Store in both Django cache and in-memory cache
        cache.set(cache_key, access_token, timeout=cache_ttl)
        _MEMORY_TOKEN_CACHE[self.environment] = {
            'token': access_token,
            'expires_at': time.time() + cache_ttl
        }

        return access_token

    def generate_password(self, timestamp: str) -> str:
        """
        Generate Daraja STK Push base64 password.
        base64(BusinessShortCode + PassKey + Timestamp)
        """
        data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode('utf-8')).decode('utf-8')

    def get_timestamp(self) -> str:
        """
        Generate current timestamp in East Africa Time (GMT+3) format YYYYMMDDHHmmss.
        """
        nairobi_tz = ZoneInfo('Africa/Nairobi')
        now = datetime.now(nairobi_tz)
        return now.strftime('%Y%m%d%H%M%S')

    def initiate_stk_push(
        self,
        phone_number: str,
        amount: int | float,
        account_reference: str = 'NyumbaHub',
        transaction_desc: str = 'Property Booking'
    ) -> dict:
        """
        Initiate Lipa Na M-Pesa Online (STK Push).
        """
        formatted_phone = format_phone_number(phone_number)
        timestamp = self.get_timestamp()
        password = self.generate_password(timestamp)
        int_amount = max(1, int(round(float(amount))))

        # If credentials are not configured and we are in sandbox/development,
        # return a simulated success payload for developer convenience
        if not self.is_configured() and self.environment == 'sandbox':
            logger.warning(
                "M-Pesa credentials not set in .env. Returning simulated sandbox STK push response."
            )
            simulated_checkout_id = f"ws_CO_DEV_{timestamp}_{formatted_phone[-4:]}"
            return {
                "MerchantRequestID": f"sim-req-{timestamp}",
                "CheckoutRequestID": simulated_checkout_id,
                "ResponseCode": "0",
                "ResponseDescription": "Success. Request accepted for processing (Dev Simulation)",
                "CustomerMessage": "Success. Request accepted for processing",
                "simulated": True,
            }

        access_token = self.get_access_token()

        # If simulated token was returned due to sandbox timeout / dev mode
        if access_token == "simulated_sandbox_token":
            logger.warning("Sandbox simulation active: Returning simulated STK push response.")
            simulated_checkout_id = f"ws_CO_DEV_{timestamp}_{formatted_phone[-4:]}"
            return {
                "MerchantRequestID": f"sim-req-{timestamp}",
                "CheckoutRequestID": simulated_checkout_id,
                "ResponseCode": "0",
                "ResponseDescription": "Success. Safaricom sandbox timed out; dev sandbox simulation activated.",
                "CustomerMessage": "Success. Request accepted for processing (Dev Simulation)",
                "simulated": True,
                "timeout_fallback": True,
            }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int_amount,
            "PartyA": formatted_phone,
            "PartyB": self.shortcode,
            "PhoneNumber": formatted_phone,
            "CallBackURL": self.callback_url,
            "AccountReference": str(account_reference)[:12],
            "TransactionDesc": str(transaction_desc)[:12]
        }

        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        logger.info(f"Dispatching Daraja STK Push to {formatted_phone} for KES {int_amount}")

        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=(10, self.timeout)
            )
            res_data = response.json()
        except requests.exceptions.Timeout as e:
            logger.warning(f"Daraja STK push timed out after {self.timeout}s: {e}")
            if self.environment == 'sandbox' and self.fallback_on_timeout:
                logger.info("Sandbox fallback: Returning simulated STK response due to STK push timeout.")
                simulated_checkout_id = f"ws_CO_TIMEOUT_{timestamp}_{formatted_phone[-4:]}"
                return {
                    "MerchantRequestID": f"sim-req-{timestamp}",
                    "CheckoutRequestID": simulated_checkout_id,
                    "ResponseCode": "0",
                    "ResponseDescription": "Success. Safaricom sandbox timed out; dev sandbox simulation activated.",
                    "CustomerMessage": "Request accepted for processing (Sandbox Fallback)",
                    "simulated": True,
                    "timeout_fallback": True,
                }
            raise DarajaTimeoutException(
                f"Safaricom Daraja STK push timed out after {self.timeout} seconds."
            ) from e
        except requests.exceptions.RequestException as e:
            logger.warning(f"Daraja STK push connection error: {e}")
            if self.environment == 'sandbox' and self.fallback_on_timeout:
                logger.info("Sandbox fallback: Returning simulated STK response due to connection error.")
                simulated_checkout_id = f"ws_CO_NETERR_{timestamp}_{formatted_phone[-4:]}"
                return {
                    "MerchantRequestID": f"sim-req-{timestamp}",
                    "CheckoutRequestID": simulated_checkout_id,
                    "ResponseCode": "0",
                    "ResponseDescription": "Success. Network error; dev sandbox simulation activated.",
                    "CustomerMessage": "Request accepted for processing (Sandbox Fallback)",
                    "simulated": True,
                    "network_fallback": True,
                }
            raise DarajaConnectionException("Could not connect to Safaricom Daraja STK push endpoint.") from e
        except Exception as e:
            logger.exception(f"Unexpected error parsing Daraja STK push response: {e}")
            raise DarajaAPIException(f"Failed to process Daraja STK Push response: {str(e)}") from e

        if response.status_code != 200 or res_data.get('ResponseCode') != '0':
            logger.error(f"Daraja STK push failed: {response.status_code} - {res_data}")
            error_msg = res_data.get('errorMessage') or res_data.get('ResponseDescription') or 'STK push failed'
            raise DarajaAPIException(error_msg, status_code=response.status_code, raw_data=res_data)

        return res_data

    def query_stk_status(self, checkout_request_id: str) -> dict:
        """
        Query status of an STK Push transaction via Daraja STK Query.
        """
        if not self.is_configured() or checkout_request_id.startswith('ws_CO_DEV_') or checkout_request_id.startswith('ws_CO_TIMEOUT_'):
            return {
                "ResponseCode": "0",
                "ResultCode": "0",
                "ResultDesc": "Simulation mode status active",
                "simulated": True
            }

        timestamp = self.get_timestamp()
        password = self.generate_password(timestamp)
        access_token = self.get_access_token()

        if access_token == "simulated_sandbox_token":
            return {
                "ResponseCode": "0",
                "ResultCode": "0",
                "ResultDesc": "Simulation mode status active",
                "simulated": True
            }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=(10, self.timeout))
            return response.json()
        except Exception as e:
            logger.warning(f"Error querying STK status: {e}")
            return {"error": str(e)}
