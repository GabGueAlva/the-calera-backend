# Testing the Alert System with Phone Numbers

## Updated Endpoint

The `/api/v1/send-alert` endpoint now **requires** a JSON body with phone numbers.

## How to Test

### Step 1: Make a Prediction First

```bash
curl -X POST http://localhost:8000/api/v1/predict
```

**Wait for it to complete** (2-3 minutes for first prediction with training).

### Step 2: Send Alert with Phone Numbers

```bash
curl -X POST http://localhost:8000/api/v1/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "phone_numbers": ["+573012592676", "+573001234567"]
  }'
```

### Expected Response

```json
{
  "status": "success",
  "message": "Alert sent successfully to 2 recipient(s)",
  "recipients": ["+573012592676", "+573001234567"]
}
```

### Expected Console Output

```
📱 ======================================================== 📱
     SENDING FROST ALERT (DAILY AVERAGE)
📱 ======================================================== 📱

[ALERT] Step 1: Retrieving today's predictions...
[ALERT] ✓ Found 1 predictions today

[ALERT] Step 2: Calculating daily average...
[REPOSITORY] Averaging 1 predictions: 33.15%
[ALERT] ✓ Daily average probability: 33.15%

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
Probability: 33.2%

Monitor conditions and be prepared.
============================================================
[MOCK TWILIO] ✓ Message 'sent' successfully (simulated)
[MOCK TWILIO] Message SID: SM_mock_1234567890123456
============================================================

[ALERT] Sending to +573001234567...

============================================================
[MOCK TWILIO] 📱 Simulated WhatsApp Message:
============================================================
From: whatsapp:+15555551234
To: whatsapp:+573001234567
------------------------------------------------------------
⚠️ **FROST WARNING** ⚠️

Possible frost conditions tonight.
Probability: 33.2%

Monitor conditions and be prepared.
============================================================
[MOCK TWILIO] ✓ Message 'sent' successfully (simulated)
[MOCK TWILIO] Message SID: SM_mock_7654321098765432
============================================================

[ALERT] ✓ Alerts sent successfully to 2 recipient(s)!
============================================================
```

## Testing Multiple Predictions (Full Workflow)

```bash
# Make 3 predictions
curl -X POST http://localhost:8000/api/v1/predict
sleep 2  # Wait a bit between predictions
curl -X POST http://localhost:8000/api/v1/predict
sleep 2
curl -X POST http://localhost:8000/api/v1/predict

# Send alert with averaged results
curl -X POST http://localhost:8000/api/v1/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "phone_numbers": ["+573012592676"]
  }'
```

You'll see it average all 3 predictions!

## API Documentation

Once your server is running, check the interactive docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You'll see the new request body format with phone numbers example.

## Production Use

When using real Twilio credentials, the same phone numbers will receive actual WhatsApp messages!
