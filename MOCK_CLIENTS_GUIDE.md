# Mock Clients Guide

## Overview

The system now includes mock clients for both TTS (sensor data) and Twilio (WhatsApp notifications) so you can test the entire frost prediction and alerting workflow without needing external service credentials.

## Mock Clients Available

### 1. MockTTSClient
**Purpose:** Generate realistic sensor data for testing
**Location:** `infrastructure/external/mock_tts_client.py`
**Status:** ✅ Currently Active

**Features:**
- Generates temperature data with realistic daily patterns
- Simulates frost conditions (temps below 0°C)
- Creates 5-minute interval data points
- Shows detailed statistics in logs

### 2. MockTwilioWhatsAppClient
**Purpose:** Simulate WhatsApp alert sending
**Location:** `infrastructure/external/mock_twilio_client.py`
**Status:** ✅ Currently Active

**Features:**
- Simulates sending WhatsApp messages
- Displays message content in console logs
- Shows from/to numbers
- No actual message sent (no Twilio charges)

## Current Configuration

In `dependencies.py`:

```python
# Line 24: TTS Client
self.tts_client = MockTTSClient()  # MOCK - for testing

# Line 28: Twilio Client
self.twilio_client = MockTwilioWhatsAppClient()  # MOCK - for testing
```

## Testing the Full Workflow

### 1. Make Predictions (8am, 12pm, 4pm)

```bash
# First prediction (will train models)
curl -X POST http://localhost:8000/api/v1/predict

# Second prediction (uses cached models - instant)
curl -X POST http://localhost:8000/api/v1/predict

# Third prediction (uses cached models - instant)
curl -X POST http://localhost:8000/api/v1/predict
```

**Expected Output:**
```
[MOCK TTS] ✓ Generated 2880 data points
[MOCK TTS] Temperature range: -2.0°C to 27.4°C
[MOCK TTS] Frost conditions detected: 152 points

[SARIMA] ✓ Model fitting completed!
[LSTM] ✓ Training completed successfully!

[PREDICTION] ✓ Hybrid probability: 33.15%
[REPOSITORY] ✓ Prediction saved (Daily count: 1/3)
```

### 2. Send Alert (5pm - after 3 predictions)

```bash
curl -X POST http://localhost:8000/api/v1/send-alert
```

**Expected Output:**
```
📱 ======================================================== 📱
     SENDING FROST ALERT (DAILY AVERAGE)
📱 ======================================================== 📱

[ALERT] ✓ Found 3 predictions today
[REPOSITORY] Averaging 3 predictions: 35.41%
[ALERT] ✓ Daily average probability: 35.41%

============================================================
[MOCK TWILIO] 📱 Simulated WhatsApp Message:
============================================================
From: whatsapp:+15555551234
To: whatsapp:+15555555678
------------------------------------------------------------
⚠️ **FROST WARNING** ⚠️

Possible frost conditions tonight.
Probability: 35.4%

Monitor conditions and be prepared.
============================================================
[MOCK TWILIO] ✓ Message 'sent' successfully (simulated)
============================================================

[ALERT] ✓ Alert sent successfully!
```

## Switching to Production

When you have real credentials:

### For TTS (Sensor Data)

In `dependencies.py` line 24:
```python
# Change from:
self.tts_client = MockTTSClient()

# To:
self.tts_client = TTSClient()
```

Then update `.env`:
```env
TTS_APPLICATION_ID=your_real_application_id
TTS_API_KEY=your_real_api_key
TTS_STORAGE_INTEGRATION_ID=your_real_storage_id
```

### For Twilio (WhatsApp Alerts)

In `dependencies.py` line 28:
```python
# Change from:
self.twilio_client = MockTwilioWhatsAppClient()

# To:
self.twilio_client = TwilioWhatsAppClient()
```

Then update `.env`:
```env
TWILIO_ACCOUNT_SID=your_real_account_sid
TWILIO_AUTH_TOKEN=your_real_auth_token
TWILIO_WHATSAPP_NUMBER=+1234567890
RECIPIENT_WHATSAPP_NUMBER=+0987654321
```

**Note:** To get valid Twilio credentials:
1. Sign up at https://www.twilio.com
2. Get your Account SID and Auth Token from the console
3. Set up WhatsApp sandbox or get a WhatsApp-enabled number
4. Verify your recipient number

## Benefits of Mock Clients

✅ **Test entire workflow without external dependencies**
✅ **No API costs during development**
✅ **Faster testing (no network calls)**
✅ **See exactly what messages would be sent**
✅ **No risk of sending spam messages**
✅ **Works offline**

## Summary

Both mock clients are currently active, allowing you to:
1. Generate realistic sensor data
2. Train and test ML models
3. Make predictions
4. See exactly what WhatsApp messages would be sent
5. Test the daily averaging logic

Everything works end-to-end without needing TTS or Twilio accounts! 🎉
