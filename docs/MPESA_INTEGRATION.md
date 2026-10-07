# Safaricom M-Pesa Daraja API Integration Guide

## Overview

TapIn integrates Safaricom M-Pesa Daraja API (Lipa Na M-Pesa Online / STK Push) to enable seamless booking deposit and rent payments for tenants.

---

## Architecture & Data Flow

```
[Tenant Browser] 
      │ 1. Enter Phone & Click "Send M-Pesa Prompt"
      ▼
[POST /api/payments/initiate/]
      │ 2. Validates & formats phone (254XXXXXXXXX)
      │ 3. Requests OAuth Token & generates base64 password
      ▼
[Safaricom Daraja API] ── STK Push ──► [Tenant's Mobile Device]
      │                                       │
      │                                       ▼
      │                                Tenant enters PIN
      │                                       │
      ▼                                       ▼
[POST /api/payments/callback/] ◄──── Webhook Result (stkCallback)
      │
      ▼
[Payment & Property DB Updated] (Status: COMPLETED / CANCELLED / FAILED)
      ▲
      │ Polling every 2.5s (up to 60s)
[Tenant Browser: GET /api/payments/status/<checkout_id>/]
```

---

## Configuration (`.env`)

In `tapin-frontend/.env`:

```env
# Safaricom Daraja API (Sandbox Mode)
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your_sandbox_consumer_key
MPESA_CONSUMER_SECRET=your_sandbox_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://your-domain.ngrok-free.app/api/payments/callback/
```

> **Note on Sandbox Credentials:**
> - `174379` is Safaricom's official public test Paybill shortcode.
> - `bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919` is the standard Safaricom sandbox passkey.
> - To get your personal `CONSUMER_KEY` and `CONSUMER_SECRET`:
>   1. Log into [Safaricom Daraja Portal](https://developer.safaricom.co.ke/).
>   2. Go to **My Apps** -> **Add New App** -> check **Lipa Na M-Pesa Sandbox**.
>   3. Copy your Consumer Key and Consumer Secret into `.env`.

---

## Local Development & Webhooks (ngrok Tunnel)

Safaricom cannot reach `localhost:8000` or `127.0.0.1:8000`. To receive real callbacks during local development:

1. Start your local Django server:
   ```bash
   python manage.py runserver 8000
   ```
2. In a separate terminal, expose your local port:
   ```bash
   ngrok http 8000
   ```
3. Copy the HTTPS forwarding URL (e.g. `https://abc1234.ngrok-free.app`) and set:
   ```env
   MPESA_CALLBACK_URL=https://abc1234.ngrok-free.app/api/payments/callback/
   ```

---

## Built-in Development Simulation Mode

When developing offline or without an active ngrok tunnel:
- If credentials are not yet configured in `.env`, the system automatically activates sandbox simulation mode.
- You can also simulate an instant Daraja confirmation callback via API:

```bash
curl -X POST http://localhost:8000/api/payments/simulate-callback/ \
  -H "Content-Type: application/json" \
  -d '{
    "checkout_request_id": "<CHECKOUT_REQUEST_ID>",
    "result_code": 0,
    "receipt_no": "TEST1234XYZ"
  }'
```

---

## API Endpoints Reference

### 1. Initiate STK Push
- **URL:** `POST /api/payments/initiate/` (or `/api/payments/stk-push/`)
- **Payload:**
  ```json
  {
    "phone": "0712345678",
    "amount": 1500,
    "property_id": 1,
    "payment_type": "booking"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "M-Pesa payment prompt sent to your phone! Please enter your M-Pesa PIN.",
    "checkout_request_id": "ws_CO_20261005_1234",
    "merchant_request_id": "MR-12345",
    "status": "PENDING",
    "phone": "254712345678",
    "amount": "1500.00"
  }
  ```

### 2. Safaricom Webhook Callback
- **URL:** `POST /api/payments/callback/`
- Called automatically by Safaricom servers with `stkCallback` payload.
- Automatically marks payment as `COMPLETED`, saves `mpesa_receipt_number`, and sets property status to `booked`.

### 3. Check Payment Status (Polling)
- **URL:** `GET /api/payments/status/<checkout_request_id>/`
- **Response (200 OK):**
  ```json
  {
    "id": 1,
    "checkout_request_id": "ws_CO_20261005_1234",
    "status": "COMPLETED",
    "amount": "1500.00",
    "phone_number": "254712345678",
    "mpesa_receipt_number": "QGH789XYZ",
    "result_code": 0,
    "property_title": "Sunset Studio Nairobi"
  }
  ```
