# Quick Test Guide - Alert System

## Problem
Predictions are stored in memory and reset when the server restarts. This makes testing the alert system difficult.

## Solution
Use the test endpoint to create mock predictions instantly!

## Quick Test Steps

### 1. Start the Server
```bash
source .venv/bin/activate && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Create Mock Predictions (Instant - No Training!)
```bash
# Create 3 mock predictions (run these commands one after another)
curl -X POST http://localhost:8000/api/v1/test/create-mock-prediction
curl -X POST http://localhost:8000/api/v1/test/create-mock-prediction
curl -X POST http://localhost:8000/api/v1/test/create-mock-prediction
```

**Response:**
```json
{
  "status": "success",
  "message": "Mock prediction created for testing",
  "prediction": {
    "probability": 0.45,
    "frost_level": "possible_frost",
    "created_at": "2025-10-29T15:30:00.123456"
  }
}
```

### 3. Send Alert
```bash
curl -X POST http://localhost:8000/api/v1/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "phone_numbers": ["+573012592676", "+573001234567"]
  }'
```

**Expected Output:**
```
📱 ======================================================== 📱
     SENDING FROST ALERT (DAILY AVERAGE)
📱 ======================================================== 📱

[ALERT] Step 1: Retrieving today's predictions...
[ALERT] ✓ Found 3 predictions today

[ALERT] Step 2: Calculating daily average...
[REPOSITORY] Averaging 3 predictions: 45.00%
[ALERT] ✓ Daily average probability: 45.00%

[ALERT] Step 3: Sending WhatsApp notifications to 2 recipient(s)...
[ALERT] Frost Level: possible_frost
[ALERT] Sending to +573012592676...

============================================================
[MOCK TWILIO] 📱 Simulated WhatsApp Message:
============================================================
From: whatsapp:+15555551234
To: whatsapp:+573012592676
------------------------------------------------------------
⚠️ **FROST WARNING** ⚠️

Possible frost conditions tonight.
Probability: 45.0%

Monitor conditions and be prepared.
============================================================
[MOCK TWILIO] ✓ Message 'sent' successfully (simulated)
[MOCK TWILIO] Message SID: SM_mock_1234567890123456
============================================================

[ALERT] Sending to +573001234567...
(same message...)

[ALERT] ✓ Alerts sent successfully to 2 recipient(s)!
============================================================
```

## Complete Test Workflow (All in One)

```bash
# Create 3 mock predictions
for i in {1..3}; do
  curl -X POST http://localhost:8000/api/v1/test/create-mock-prediction
  sleep 0.5
done

# Send alert
curl -X POST http://localhost:8000/api/v1/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "phone_numbers": ["+573012592676"]
  }'
```

## Benefits of Mock Predictions

✅ **Instant** - No 2-3 minute wait for ML training
✅ **Consistent** - Always creates same probability (45%)
✅ **Repeatable** - Test alert system multiple times quickly
✅ **No ML needed** - Bypasses SARIMA and LSTM completely

## When to Use Real Predictions vs Mock

| Scenario | Use |
|----------|-----|
| Testing alert system | Mock predictions (this endpoint) |
| Testing ML models | Real predictions (`/api/v1/predict`) |
| Testing averaging logic | Mock predictions (faster) |
| Testing phone numbers | Mock predictions (faster) |
| Production | Real predictions only |

## Test Endpoint Details

**Endpoint:** `POST /api/v1/test/create-mock-prediction`

**What it creates:**
- Probability: 45%
- Frost Level: POSSIBLE_FROST
- SARIMA: 35%
- LSTM: 55%
- Created at: Current UTC time

**Perfect for:**
- Quick testing of alert flow
- Testing multiple predictions averaging
- Testing multiple phone numbers
- Demos

## Important Notes

⚠️ **This is a TEST endpoint** - Remove or disable in production!

⚠️ **Memory only** - Predictions reset when server restarts

⚠️ **Same values** - Each mock has same probabilities (45%)
