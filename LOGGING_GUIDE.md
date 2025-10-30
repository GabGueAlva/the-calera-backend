# Frost Prediction System - Logging Guide

This document explains the detailed logging added to the system so you can track exactly where the algorithm is at any point.

## Overview

The system now includes comprehensive logging at every stage of the prediction process. You'll see exactly:
- Which part of the process is running (SARIMA, LSTM, Data Generation)
- Progress through LSTM epochs (1/50, 2/50, etc.)
- When models are using cached versions (instant)
- Data statistics and prediction results

## Sample Output: First Prediction (Training Required)

When you run the first prediction of the day, you'll see output like this:

```
============================================================
[MOCK TTS] Using Mock TTS Client for testing
[MOCK TTS] Simulated sensor data will be generated
============================================================

============================================================
[MOCK TTS] Generating sensor data...
[MOCK TTS] Time range: 2025-10-19 14:00:00 to 2025-10-29 14:00:00
============================================================
[MOCK TTS] Base temperature for this generation: 14.3°C
[MOCK TTS] Generating data points (one every 5 minutes)...
------------------------------------------------------------
[MOCK TTS] ✓ Generated 2880 data points
[MOCK TTS] Temperature range: -1.8°C to 21.5°C
[MOCK TTS] Frost conditions detected: 142 points at or below 0°C
============================================================

🌡️ ======================================================== 🌡️
     STARTING FROST PREDICTION PROCESS
🌡️ ======================================================== 🌡️

[PREDICTION] Step 1: Fetching sensor data from last 10 days...
[PREDICTION] ✓ Retrieved 2880 sensor readings

[PREDICTION] Step 2: Running SARIMA model prediction...

============================================================
[SARIMA] Preparing temperature data for training...
============================================================
[SARIMA] Temperature series prepared: 2880 data points
[SARIMA] Building SARIMAX model with order=(0,0,1) seasonal=(0,1,2,144)...
[SARIMA] Model structure created
[SARIMA] Starting model fitting (this will take 20-40 seconds)...
------------------------------------------------------------
------------------------------------------------------------
[SARIMA] ✓ Model fitting completed successfully!
============================================================

[PREDICTION] ✓ SARIMA probability: 34.56%

[PREDICTION] Step 3: Running LSTM model prediction...

============================================================
[LSTM] Preparing data for training...
============================================================
[LSTM] Data prepared: 2880 data points
[LSTM] Data scaled successfully
[LSTM] Created 2736 sequences for training
[LSTM] Model architecture built
[LSTM] Starting training with 50 epochs (this will take 2-3 minutes)...
------------------------------------------------------------
  [LSTM] Starting epoch 1/50...
  [LSTM] Epoch 1/50 completed - Loss: 0.2456, Val Loss: 0.2234
  [LSTM] Starting epoch 2/50...
  [LSTM] Epoch 2/50 completed - Loss: 0.2101, Val Loss: 0.1987
  [LSTM] Starting epoch 3/50...
  [LSTM] Epoch 3/50 completed - Loss: 0.1876, Val Loss: 0.1745
  ...
  [LSTM] Starting epoch 48/50...
  [LSTM] Epoch 48/50 completed - Loss: 0.0543, Val Loss: 0.0512
  [LSTM] Starting epoch 49/50...
  [LSTM] Epoch 49/50 completed - Loss: 0.0541, Val Loss: 0.0510
  [LSTM] Starting epoch 50/50...
  [LSTM] Epoch 50/50 completed - Loss: 0.0539, Val Loss: 0.0508
------------------------------------------------------------
[LSTM] ✓ Training completed successfully!
============================================================

[PREDICTION] ✓ LSTM probability: 42.78%

[PREDICTION] Step 4: Calculating hybrid prediction...
[PREDICTION] Hybrid formula: (SARIMA * 0.5) + (LSTM * 0.5)
[PREDICTION] ✓ Hybrid probability: 38.67%

[REPOSITORY] ✓ Prediction saved (Daily count: 1/3)
============================================================
✓ PREDICTION COMPLETE
  Frost Level: POSSIBLE_FROST
  Probability: 38.67%
============================================================
```

## Sample Output: Second & Third Predictions (Cached Models)

On subsequent predictions (12pm, 4pm), the models are already trained and cached:

```
🌡️ ======================================================== 🌡️
     STARTING FROST PREDICTION PROCESS
🌡️ ======================================================== 🌡️

[PREDICTION] Step 1: Fetching sensor data from last 10 days...

============================================================
[MOCK TTS] Generating sensor data...
[MOCK TTS] Time range: 2025-10-19 16:00:00 to 2025-10-29 16:00:00
============================================================
[MOCK TTS] Base temperature for this generation: 15.7°C
[MOCK TTS] Generating data points (one every 5 minutes)...
------------------------------------------------------------
[MOCK TTS] ✓ Generated 2880 data points
[MOCK TTS] Temperature range: 0.2°C to 23.1°C
[MOCK TTS] Frost conditions detected: 89 points at or below 0°C
============================================================

[PREDICTION] ✓ Retrieved 2880 sensor readings

[PREDICTION] Step 2: Running SARIMA model prediction...
[SARIMA] ⚡ Using cached model (already trained, prediction will be instant)
[PREDICTION] ✓ SARIMA probability: 28.34%

[PREDICTION] Step 3: Running LSTM model prediction...
[LSTM] ⚡ Using cached model (already trained, prediction will be instant)
[PREDICTION] ✓ LSTM probability: 31.22%

[PREDICTION] Step 4: Calculating hybrid prediction...
[PREDICTION] Hybrid formula: (SARIMA * 0.5) + (LSTM * 0.5)
[PREDICTION] ✓ Hybrid probability: 29.78%

[REPOSITORY] ✓ Prediction saved (Daily count: 2/3)
============================================================
✓ PREDICTION COMPLETE
  Frost Level: POSSIBLE_FROST
  Probability: 29.78%
============================================================
```

**Notice:** The second and third predictions complete in ~1 second because they use cached models!

## Sending Alert (After 4pm, at 5pm)

When the scheduler runs the alert job after collecting all 3 predictions:

```
📱 ======================================================== 📱
     SENDING FROST ALERT (DAILY AVERAGE)
📱 ======================================================== 📱

[ALERT] Step 1: Retrieving today's predictions...
[ALERT] ✓ Found 3 predictions today

[ALERT] Step 2: Calculating daily average...
[REPOSITORY] Averaging 3 predictions: 35.41%
[ALERT] ✓ Daily average probability: 35.41%

[ALERT] Step 3: Sending WhatsApp notification...
[ALERT] Frost Level: POSSIBLE_FROST
WhatsApp message sent successfully. SID: SM123456789
[ALERT] ✓ Alert sent successfully!
============================================================
```

## Key Logging Tags

- `[MOCK TTS]` - Mock data generation (remove when using real TTS)
- `[PREDICTION]` - Main prediction workflow steps
- `[SARIMA]` - SARIMA model operations
- `[LSTM]` - LSTM model operations (includes epoch progress)
- `[REPOSITORY]` - Database/storage operations
- `[ALERT]` - Alert sending process

## Understanding the Flow

### First Prediction (~3 minutes)
1. Generate/fetch sensor data (~1 second)
2. Train SARIMA model (~30 seconds)
3. Train LSTM model (~2 minutes, 50 epochs)
4. Calculate hybrid prediction (~1 second)
5. Save prediction

### Subsequent Predictions (~1 second each)
1. Generate/fetch sensor data (~1 second)
2. Use cached SARIMA (instant)
3. Use cached LSTM (instant)
4. Calculate hybrid prediction (instant)
5. Save prediction

### Daily Alert
1. Retrieve all predictions from today
2. Calculate average of all probabilities
3. Send WhatsApp with averaged prediction

## Tips

- Watch for the ⚡ emoji - means cached models are being used (fast!)
- Watch for ✓ checkmarks - means that step completed successfully
- Watch for ✗ - means an error occurred
- Epoch numbers show LSTM training progress (1/50, 2/50, etc.)
- Loss values decreasing = model is learning well
- Daily count (1/3, 2/3, 3/3) shows how many predictions have been made today
