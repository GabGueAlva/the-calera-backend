# AI-Powered Frost Prediction System
## International Congress Presentation Guide

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Agricultural Challenge](#2-the-agricultural-challenge)
3. [System Overview](#3-system-overview)
4. [System Architecture](#4-system-architecture)
5. [Data Collection & IoT Integration](#5-data-collection--iot-integration)
6. [Machine Learning Algorithms](#6-machine-learning-algorithms)
7. [Prediction Workflow](#7-prediction-workflow)
8. [Decision Rules & Alert System](#8-decision-rules--alert-system)
9. [Automation & Scheduling](#9-automation--scheduling)
10. [Technical Stack](#10-technical-stack)
11. [Real-World Implementation](#11-real-world-implementation)
12. [Results & Impact](#12-results--impact)
13. [Future Enhancements](#13-future-enhancements)
14. [Conclusion](#14-conclusion)

---

## 1. Executive Summary

This project presents an **AI-powered frost prediction system** that combines IoT sensor technology with advanced machine learning algorithms to provide timely frost warnings to farmers. The system integrates real-time meteorological data from The Things Stack (TTS) IoT network and employs a hybrid machine learning approach combining SARIMA and LSTM models to predict frost conditions with high accuracy.

**Key Features:**
- Real-time IoT sensor data collection (temperature, humidity, wind speed)
- Dual machine learning models (SARIMA + LSTM) with hybrid fusion
- Automated daily predictions (3:00 AM, 12:00 PM, 4:00 PM)
- WhatsApp notifications to farmers at 5:00 PM daily
- Clean Architecture design for scalability and maintainability

---

## 2. The Agricultural Challenge

### Problem Statement

Frost is one of the most devastating weather phenomena for agriculture, causing:
- **Crop damage and loss**: Freezing temperatures destroy plant cells
- **Economic impact**: Significant financial losses for farmers
- **Food security concerns**: Reduced crop yields affect food supply
- **Limited warning time**: Traditional forecasts lack precision for micro-climates

### Why This Matters

Farmers need:
- **Accurate predictions**: Know when frost will occur with high confidence
- **Timely alerts**: Sufficient time to implement protective measures
- **Actionable information**: Clear guidance on risk levels
- **Accessible technology**: Easy-to-use system without technical barriers

---

## 3. System Overview

### What It Does

The system provides automated frost predictions by:
1. **Collecting** real-time meteorological data from IoT sensors
2. **Analyzing** historical patterns using machine learning
3. **Predicting** frost probability for the next 12-24 hours
4. **Notifying** farmers via WhatsApp with actionable alerts

### How It Works

```
IoT Sensors → Data Collection → ML Models → Prediction → WhatsApp Alert
   (TTS)      (Every 5 min)    (SARIMA+LSTM)  (3x daily)   (5:00 PM)
```

### Core Components

1. **Data Layer**: IoT sensors + The Things Stack integration
2. **Intelligence Layer**: SARIMA + LSTM machine learning models
3. **Application Layer**: FastAPI backend with automated scheduling
4. **Notification Layer**: Twilio WhatsApp messaging service

---

## 4. System Architecture

### Clean Architecture (Onion Architecture)

The system follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│              Interfaces Layer (API)                  │
│     FastAPI Controllers, Schemas, Middleware         │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│          Application Layer (Use Cases)               │
│    Prediction Generation, Alert Sending, etc.       │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│            Domain Layer (Business Logic)             │
│   Entities, Repositories, Service Interfaces         │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│       Infrastructure Layer (External Services)       │
│   TTS Client, ML Models, Twilio, Database            │
└─────────────────────────────────────────────────────┘
```

### Benefits of This Architecture

- **Modularity**: Each layer has a single responsibility
- **Testability**: Business logic independent of external services
- **Maintainability**: Easy to update or replace components
- **Scalability**: Can add new models or notification channels easily
- **Dependency Inversion**: Core logic doesn't depend on frameworks

---

## 5. Data Collection & IoT Integration

### The Things Stack (TTS) Integration

**The Things Stack** is a LoRaWAN network server that manages IoT sensor devices.

#### Data Sources

The system collects three critical meteorological parameters:
- **Temperature (°C)**: Primary indicator for frost risk
- **Humidity (%)**: Affects dew point and frost formation
- **Wind Speed (m/s)**: Wind reduces frost likelihood

#### Data Collection Process

1. **Sensor Transmission**: IoT sensors transmit data every 5 minutes via LoRaWAN
2. **TTS Reception**: The Things Stack receives and stores sensor data
3. **API Integration**: Backend fetches data via TTS Storage API
4. **Data Processing**: Raw data is cleaned, validated, and stored
5. **Continuous Updates**: System maintains 10-day rolling window of data

#### TTS API Integration

```python
# Endpoint Structure
GET /api/v3/as/applications/{application_id}/packages/storage/{storage_id}/uplink_message

# Parameters
- field_mask: Specifies which fields to return
- after: Start timestamp (ISO 8601)
- before: End timestamp (ISO 8601)
- limit: Maximum records (up to 10,000)
```

#### Data Quality

- **Resampling**: Data resampled to consistent 5-minute intervals
- **Interpolation**: Missing values interpolated from neighboring points
- **Validation**: Outliers and invalid readings filtered out
- **Timestamp**: All data timestamped in UTC for consistency

---

## 6. Machine Learning Algorithms

The system employs a **hybrid approach** combining two complementary machine learning models:

### 6.1 SARIMA Model (Seasonal AutoRegressive Integrated Moving Average)

#### What It Is

SARIMA is a classical **time series forecasting** model that captures seasonal patterns and trends in temperature data.

#### Configuration

```
SARIMA(0,0,1)(0,1,2,144)
```

**Parameters Explained:**
- **Non-seasonal**: (p=0, d=0, q=1)
  - p=0: No autoregressive terms
  - d=0: No differencing needed
  - q=1: One moving average term
- **Seasonal**: (P=0, D=1, Q=2, m=144)
  - P=0: No seasonal autoregressive terms
  - D=1: First-order seasonal differencing
  - Q=2: Two seasonal moving average terms
  - m=144: Seasonal period (24 hours × 6 intervals/hour = 144 five-minute intervals)

#### How It Works

1. **Data Preparation**:
   - Uses 10 days of historical temperature data
   - Resamples to 5-minute intervals (288 points/day)
   - Total of ~2,880 data points

2. **Model Training**:
   - Fits SARIMAX model to temperature series
   - Captures daily temperature cycles (diurnal patterns)
   - Identifies seasonal patterns (day/night temperature variations)

3. **Prediction**:
   - Forecasts next 12 intervals (1 hour ahead)
   - Extracts minimum forecasted temperature
   - Converts temperature to frost probability

#### Probability Calculation

```python
if min_temp <= 0°C:
    probability = min(0.9, max(0.7, (2 - min_temp) / 4))
elif min_temp <= 4°C:
    probability = 0.3 + (4 - min_temp) * 0.1
else:
    probability = max(0.05, 0.3 - (min_temp - 4) * 0.05)
```

**Logic:**
- Below 0°C: 70-90% probability (high risk)
- 0-4°C: 30-70% probability (moderate risk)
- Above 4°C: 5-30% probability (low risk)

#### Strengths

- Excellent at capturing **temporal patterns**
- Understands **seasonal cycles** (daily temperature variations)
- Computationally efficient (fits in 20-40 seconds)
- Interpretable and well-established methodology

#### Limitations

- Only uses temperature (univariate)
- Assumes patterns continue (struggles with sudden changes)
- Linear relationships only

---

### 6.2 LSTM Model (Long Short-Term Memory Neural Network)

#### What It Is

LSTM is a type of **recurrent neural network** (RNN) that can learn complex patterns from sequential data using multiple features.

#### Architecture

```python
Sequential([
    LSTM(50 units, return_sequences=True, L2 regularization)
    Dropout(0.3)
    LSTM(50 units, return_sequences=False, L2 regularization)
    Dropout(0.3)
    Dense(25 units, ReLU activation, L2 regularization)
    Dropout(0.2)
    Dense(1 unit, Sigmoid activation)
])
```

**Layer Breakdown:**
1. **First LSTM Layer**: 50 units, processes sequences and passes to next layer
2. **Dropout 30%**: Prevents overfitting by randomly dropping connections
3. **Second LSTM Layer**: 50 units, produces final hidden state
4. **Dropout 30%**: Additional regularization
5. **Dense Layer**: 25 units with ReLU activation for non-linearity
6. **Dropout 20%**: Final regularization
7. **Output Layer**: Single unit with sigmoid (outputs 0-1 probability)

#### Input Features (Multivariate)

The LSTM model uses **three meteorological parameters**:
1. **Temperature (°C)**
2. **Humidity (%)**
3. **Wind Speed (m/s)**

#### Sequence Length

- **144 time steps** = 12 hours of 5-minute intervals
- Model looks at 12 hours of historical data to predict next hour

#### How It Works

1. **Data Preparation**:
   - Creates sequences of 144 time steps (12 hours)
   - Each time step contains [temperature, humidity, wind_speed]
   - Data scaled using MinMaxScaler (0-1 range)

2. **Target Creation**:
   - For each sequence, looks ahead 12 intervals (1 hour)
   - Calculates minimum temperature in next hour
   - Converts to continuous frost probability (0.0-1.0)

3. **Training**:
   - 50 epochs with early stopping (patience=10)
   - Batch size: 32
   - Validation split: 20%
   - Optimizer: Adam (learning_rate=0.001)
   - Loss function: MSE (Mean Squared Error)
   - Metric: MAE (Mean Absolute Error)

4. **Prediction**:
   - Takes last 12 hours of data
   - Feeds through trained network
   - Outputs frost probability (0.0-1.0)

#### Probability Target Formula

```python
if min_temp <= 0°C:
    frost_prob = min(0.9, max(0.7, (2 - min_temp) / 4))
elif min_temp <= 4°C:
    frost_prob = 0.3 + (4 - min_temp) * 0.1  # 0.3 to 0.7
else:
    frost_prob = max(0.05, 0.3 - (min_temp - 4) * 0.05)
```

#### Regularization Techniques

- **L2 Regularization**: Penalizes large weights (0.001)
- **Dropout**: Randomly drops neurons during training
- **Early Stopping**: Stops if validation loss doesn't improve for 10 epochs

#### Strengths

- **Multivariate**: Uses temperature, humidity, and wind speed
- **Non-linear patterns**: Captures complex relationships
- **Temporal dependencies**: Understands long-term patterns (12 hours)
- **Adaptive**: Learns from data without explicit programming

#### Limitations

- Requires substantial training time (2-3 minutes with 50 epochs)
- More computationally expensive than SARIMA
- "Black box" nature (less interpretable)
- Needs sufficient data for training

---

### 6.3 Hybrid Fusion Model

#### Why Hybrid?

**Combining SARIMA and LSTM leverages the strengths of both:**

| Model | Strengths | Weaknesses |
|-------|-----------|------------|
| SARIMA | Fast, interpretable, good at seasonal patterns | Univariate, linear |
| LSTM | Multivariate, captures complex patterns | Slow, less interpretable |
| **HYBRID** | **Best of both worlds** | **Minimal** |

#### Fusion Formula

```python
hybrid_probability = (sarima_probability × 0.4) + (lstm_probability × 0.6)
```

**Weighted average** with LSTM receiving higher weight (60%) and SARIMA 40%.

#### Why These Weights?

- **LSTM Strength (60%)**: Multivariate approach captures complex interactions between temperature, humidity, and wind
- **SARIMA Complement (40%)**: Provides temporal pattern validation and seasonal consistency
- **Robustness**: If one model has unusual output, the other compensates
- **Performance**: Weighted approach gives more influence to the more sophisticated model

#### Example Calculation

```
Scenario: Predicting frost for tonight

SARIMA Model:
- Forecasted min temp: 1°C
- Probability: 0.65 (65%)

LSTM Model:
- Temperature: 2°C, Humidity: 85%, Wind: 0.5 m/s
- Probability: 0.72 (72%)

Hybrid Fusion:
- (0.65 × 0.4) + (0.72 × 0.6) = 0.692
- Final Probability: 69.2%
```

#### Benefits of Hybrid Approach

1. **Improved Accuracy**: Reduces individual model errors
2. **Robustness**: Less sensitive to outliers or model-specific weaknesses
3. **Confidence**: Consensus between models increases reliability
4. **Complementary**: SARIMA catches temporal patterns, LSTM catches multivariate relationships

---

### 6.4 Model Comparison Summary

| Aspect | SARIMA | LSTM | Hybrid |
|--------|--------|------|--------|
| **Input Features** | Temperature only | Temp + Humidity + Wind | Both |
| **Training Time** | 20-40 seconds | 2-3 minutes | Combined |
| **Forecast Horizon** | 1 hour (12 intervals) | 1 hour (12 intervals) | 1 hour |
| **Data Required** | 10 days minimum | 10 days minimum | 10 days minimum |
| **Pattern Type** | Linear, seasonal | Non-linear, complex | Both |
| **Interpretability** | High | Low | Medium |
| **Computational Cost** | Low | High | Medium |

---

## 7. Prediction Workflow

### Complete Prediction Process

The system generates predictions through a **5-step automated workflow**:

```
Step 1: Data Collection
         ↓
Step 2: SARIMA Prediction
         ↓
Step 3: LSTM Prediction
         ↓
Step 4: Hybrid Fusion
         ↓
Step 5: Alert Classification
```

### Step-by-Step Breakdown

#### Step 1: Data Collection

```python
time_range = TimeRange.last_n_days(10)  # Last 10 days
sensor_data = fetch_from_TTS(time_range)
# Result: ~2,880 sensor readings (288 per day × 10 days)
```

**Activities:**
- Connect to The Things Stack API
- Retrieve 10 days of sensor data
- Filter and validate readings
- Resample to 5-minute intervals
- Interpolate missing values

**Output:** Clean dataset with temperature, humidity, wind speed

---

#### Step 2: SARIMA Prediction

```python
# Data Preparation
temperature_series = extract_temperature(sensor_data)
resampled_series = resample_to_5min(temperature_series)

# Model Training (if not cached)
model = SARIMAX(resampled_series, order=(0,0,1), seasonal_order=(0,1,2,144))
fitted_model = model.fit()

# Forecasting
forecast = fitted_model.forecast(steps=12)  # Next 1 hour
min_forecast_temp = min(forecast)

# Probability Calculation
sarima_probability = calculate_frost_probability(min_forecast_temp)
```

**Output:** SARIMA probability (e.g., 0.62 = 62%)

---

#### Step 3: LSTM Prediction

```python
# Data Preparation
df = prepare_multivariate_data(sensor_data)  # Temp, Humidity, Wind
scaled_data = MinMaxScaler().fit_transform(df)

# Sequence Creation
sequences = create_sequences(scaled_data, sequence_length=144)
# Result: [batch_size, 144, 3] tensor

# Model Training (if not cached)
model = build_lstm_model()
model.fit(sequences, targets, epochs=50, validation_split=0.2)

# Prediction
last_sequence = scaled_data[-144:]  # Last 12 hours
lstm_probability = model.predict(last_sequence)
```

**Output:** LSTM probability (e.g., 0.71 = 71%)

---

#### Step 4: Hybrid Fusion

```python
# Weighted average (LSTM 60%, SARIMA 40%)
hybrid_probability = (sarima_probability * 0.4) + (lstm_probability * 0.6)

# Example:
# SARIMA: 0.62 (62%)
# LSTM:   0.71 (71%)
# HYBRID: (0.62 × 0.4) + (0.71 × 0.6) = 0.674 (67.4%)
```

**Output:** Final frost probability (e.g., 0.674 = 67.4%)

---

#### Step 5: Alert Classification

```python
def determine_frost_level(probability: float) -> FrostLevel:
    if probability > 0.70:
        return FrostLevel.FROST_EXPECTED     # High risk
    elif probability < 0.30:
        return FrostLevel.NO_FROST           # Low risk
    else:
        return FrostLevel.POSSIBLE_FROST     # Medium risk

# Example: 66.5% → POSSIBLE_FROST
```

**Output:** Frost level classification + probability

---

### Complete Example Execution

```
🌡️ ======================================================== 🌡️
           STARTING FROST PREDICTION PROCESS
🌡️ ======================================================== 🌡️

[PREDICTION] Step 1: Fetching sensor data from last 10 days...
[PREDICTION] ✓ Retrieved 2,847 sensor readings

[PREDICTION] Step 2: Running SARIMA model prediction...
[SARIMA] Temperature series prepared: 2,880 data points
[SARIMA] Building SARIMAX model with order=(0,0,1) seasonal=(0,1,2,144)...
[SARIMA] Model fitting completed successfully!
[PREDICTION] ✓ SARIMA probability: 62%

[PREDICTION] Step 3: Running LSTM model prediction...
[LSTM] Data prepared: 2,880 data points
[LSTM] Created 2,736 sequences for training
[LSTM] Training completed successfully!
[PREDICTION] ✓ LSTM probability: 71%

[PREDICTION] Step 4: Calculating hybrid prediction...
[PREDICTION] Hybrid formula: (SARIMA * 0.4) + (LSTM * 0.6)
[PREDICTION] ✓ Hybrid probability: 67.4%

============================================================
✓ PREDICTION COMPLETE
  Frost Level: possible_frost
  Probability: 67.4%
============================================================
```

---

## 8. Decision Rules & Alert System

### Frost Level Classification

The system uses **three-tier risk classification**:

```python
if probability > 70%:
    ❄️ FROST EXPECTED (High Risk)
elif probability < 30%:
    ✅ NO FROST EXPECTED (Low Risk)
else:
    ⚠️ POSSIBLE FROST (Medium Risk)
```

### Risk Categories

#### 1. FROST EXPECTED (>70%)

**Meaning:** High confidence frost will occur

**WhatsApp Message (Spanish):**
```
¡Hola! [Farmer Name]

🥶 *ALERTA DE HELADA* 🥶

¡Se esperan heladas esta noche!
Probabilidad: 75.5%

Por favor, tome medidas de protección para sus cultivos.
```

**Recommended Actions:**
- Activate frost protection measures immediately
- Cover sensitive crops
- Deploy wind machines or heaters if available
- Monitor temperature throughout the night

---

#### 2. POSSIBLE FROST (30-70%)

**Meaning:** Uncertain conditions, frost may occur

**WhatsApp Message (Spanish):**
```
¡Hola! [Farmer Name]

⚠️ *ADVERTENCIA DE HELADA* ⚠️

Posibles condiciones de helada esta noche.
Probabilidad: 55.0%

Monitoree las condiciones y esté preparado.
```

**Recommended Actions:**
- Stay alert and monitor conditions
- Prepare protection equipment
- Check forecast updates
- Be ready to act if conditions worsen

---

#### 3. NO FROST EXPECTED (<30%)

**Meaning:** Low confidence frost will occur

**WhatsApp Message (Spanish):**
```
¡Hola! [Farmer Name]

✅ *SIN HELADA ESPERADA* ✅

No se esperan heladas esta noche.
Probabilidad: 15.0%

¡Las condiciones se ven favorables!
```

**Recommended Actions:**
- Normal operations
- No special measures needed
- Routine crop monitoring

---

### Daily Alert Aggregation

#### Why Daily Average?

The system generates predictions **3 times per day** (3 AM, 12 PM, 4 PM), but sends only **one alert** at 5 PM using the **daily average probability**.

**Rationale:**
- Reduces alert fatigue
- Provides consolidated risk assessment
- Captures how risk evolves throughout the day
- More reliable than single snapshot

#### Calculation Method

```python
# Example: Three predictions made today
prediction_1 (3:00 AM):  62% probability
prediction_2 (12:00 PM): 58% probability
prediction_3 (4:00 PM):  71% probability

# Daily average
daily_avg = (62% + 58% + 71%) / 3 = 63.7%

# Alert sent at 5:00 PM
Classification: POSSIBLE_FROST (30-70%)
```

---

### Notification System Architecture

```
┌──────────────────────────────────────────────────────┐
│           Prediction Repository                       │
│    (Stores all daily predictions with timestamps)    │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│         Calculate Daily Average Probability           │
│     (Average of all predictions made today)           │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│          Determine Frost Level                        │
│     (Apply >70%, <30% classification rules)           │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│          Farmer Repository                            │
│   (Get registered farmers with phone numbers)         │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│     Twilio WhatsApp Notification Service              │
│  (Send personalized alerts to each farmer)            │
└──────────────────────────────────────────────────────┘
```

---

### Personalization

Each farmer receives a **personalized message** with their name:

```python
# Without registration
"¡Hola! [Generic greeting]"

# With registration
"¡Hola! Gabriela Guevara"
"¡Hola! María González"
```

**Farmer Data Structure:**
```json
{
  "first_name": "Gabriela",
  "last_name": "Guevara",
  "phone_number": "+573012592676",
  "lot_address": "Finca La Esperanza, Vereda El Bosque",
  "registered_at": "2025-10-29T17:33:25.785674"
}
```

---

## 9. Automation & Scheduling

### Automated Job Schedule

The system runs **fully automated** with the following schedule:

```python
# Prediction Jobs (3 times daily)
3:00 AM   → Prediction #1 (early morning forecast)
12:00 PM  → Prediction #2 (midday update)
4:00 PM   → Prediction #3 (evening forecast)

# Alert Job (once daily)
5:00 PM   → Send WhatsApp Alert (daily average)

# Data Update Job (continuous)
Every 5 minutes → Update sensor data from TTS
```

### Scheduling Technology

**APScheduler** (Advanced Python Scheduler) - AsyncIO implementation

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

# Add prediction jobs
scheduler.add_job(run_prediction_job, CronTrigger(hour=3, minute=0))
scheduler.add_job(run_prediction_job, CronTrigger(hour=12, minute=0))
scheduler.add_job(run_prediction_job, CronTrigger(hour=16, minute=0))

# Add alert job
scheduler.add_job(send_daily_alert_job, CronTrigger(hour=17, minute=0))

# Add data update job
scheduler.add_job(update_sensor_data, CronTrigger(minute="*/5"))

scheduler.start()
```

### Daily Workflow Timeline

```
00:00 ─────────────────────────────────────────────── 24:00
       │           │              │         │
     3:00        12:00          16:00     17:00
       │           │              │         │
   Prediction  Prediction    Prediction  Alert
      #1          #2            #3       Sent
       │           │              │         │
       └───────────┴──────────────┴─────────┘
              Daily Average Calculated
```

### Why This Schedule?

**3:00 AM Prediction:**
- Captures overnight cooling
- Early warning before dawn (coldest time)

**12:00 PM Prediction:**
- Midday update with new data
- Adjusts forecast based on morning conditions

**4:00 PM Prediction:**
- Final prediction before nightfall
- Most accurate with full day's data

**5:00 PM Alert:**
- Sent after all predictions complete
- Farmers have time to prepare before evening
- Daily average provides consolidated risk assessment

---

### Model Caching Strategy

To optimize performance, **trained models are cached** in memory:

```python
# First prediction of the day
[SARIMA] Building model... (20-40 seconds)
[LSTM] Training model... (2-3 minutes)

# Subsequent predictions
[SARIMA] ⚡ Using cached model (instant)
[LSTM] ⚡ Using cached model (instant)
```

**Benefits:**
- Faster predictions (seconds vs minutes)
- Reduced CPU usage
- Consistent model across daily predictions

**Cache Validity:**
- Models cached until server restart
- Updated when significant data changes detected

---

## 10. Technical Stack

### Backend Framework

**FastAPI** (Python)
- Modern, fast web framework
- Automatic API documentation (Swagger/OpenAPI)
- Type hints and validation with Pydantic
- Async support for concurrent operations

### Machine Learning Libraries

**SARIMA:**
- `statsmodels` 0.14.0 - Statistical time series modeling
- `pandas` 2.1.4 - Data manipulation
- `numpy` 1.24.3 - Numerical computing

**LSTM:**
- `tensorflow` 2.13.0 - Deep learning framework
- `keras` (included in TensorFlow) - High-level neural network API
- `scikit-learn` 1.3.2 - Data preprocessing and scaling

### External Services

**IoT Integration:**
- **The Things Stack (TTS)** - LoRaWAN network server
- `httpx` 0.25.2 - Async HTTP client for API calls

**Notifications:**
- **Twilio WhatsApp API** - Message delivery
- `twilio` 8.10.0 - Official Python SDK

### Scheduling & Async

- `apscheduler` 3.10.4 - Job scheduling
- `asyncio` (Python built-in) - Asynchronous programming

### Configuration

- `python-dotenv` 1.0.0 - Environment variable management
- `pydantic-settings` 2.1.0 - Settings validation

### API & Validation

- `pydantic` 2.5.0 - Data validation and serialization
- `uvicorn` 0.24.0 - ASGI server for FastAPI

---

### System Requirements

**Python Version:** 3.9+

**Memory:**
- Minimum: 2 GB RAM
- Recommended: 4 GB RAM (for TensorFlow)

**Storage:**
- Application: ~500 MB
- Models: ~100 MB
- Data: ~50 MB (10 days of sensor data)

**Network:**
- Stable internet connection for TTS and Twilio APIs
- Outbound HTTPS (443) access required

---

### Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                  LoRaWAN Sensors                     │
│         (Temperature, Humidity, Wind Speed)          │
└───────────────────────┬─────────────────────────────┘
                        │ LoRaWAN Protocol
                        ▼
┌─────────────────────────────────────────────────────┐
│            The Things Stack (TTS)                    │
│          (IoT Network Server & Storage)              │
└───────────────────────┬─────────────────────────────┘
                        │ HTTPS API
                        ▼
┌─────────────────────────────────────────────────────┐
│          FastAPI Backend (This System)               │
│  ┌──────────────────────────────────────────────┐  │
│  │ Data Collection → ML Models → Predictions    │  │
│  │   (Scheduler runs 24/7 automated jobs)        │  │
│  └──────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────┘
                        │ HTTPS API
                        ▼
┌─────────────────────────────────────────────────────┐
│              Twilio WhatsApp API                     │
└───────────────────────┬─────────────────────────────┘
                        │ WhatsApp Messages
                        ▼
┌─────────────────────────────────────────────────────┐
│                   Farmers                            │
│            (Receive alerts on phones)                │
└─────────────────────────────────────────────────────┘
```

---

## 11. Real-World Implementation

### Current Deployment

**Location:** Rural agricultural area (Colombia)
**Coverage:** Multiple farm lots (fincas)
**Active Users:** 2 registered farmers (scalable to hundreds)

### Registered Farmers

```json
[
  {
    "name": "Gabriela Guevara",
    "phone": "+573012592676",
    "farm": "Finca La Esperanza, Vereda El Bosque",
    "registered": "October 29, 2025"
  },
  {
    "name": "María González",
    "phone": "+573001234567",
    "farm": "Finca El Paraíso, Lote 24",
    "registered": "October 29, 2025"
  }
]
```

### Sensor Network

**Device Type:** LoRaWAN environmental sensors
**Transmission Interval:** Every 5 minutes
**Network:** The Things Stack (TTS) LoRaWAN gateway
**Coverage Area:** Multiple farm lots within LoRaWAN range

**Measured Parameters:**
- Temperature: °C (Celsius)
- Humidity: % (Relative humidity)
- Wind Speed: m/s (Meters per second)

---

### API Endpoints

The system exposes several REST API endpoints:

#### 1. Webhook Endpoint
```
POST /api/v1/webhook
```
Receives real-time sensor data from The Things Stack.

**Use Case:** TTS sends uplink messages when sensors transmit data

---

#### 2. Manual Prediction
```
POST /api/v1/predict
```
Manually trigger a frost prediction (outside scheduled times).

**Use Case:** On-demand prediction for testing or immediate risk assessment

**Response Example:**
```json
{
  "probability": 0.665,
  "frost_level": "possible_frost",
  "model_type": "hybrid",
  "sarima_probability": 0.62,
  "lstm_probability": 0.71,
  "created_at": "2025-10-31T16:00:00Z"
}
```

---

#### 3. Send Alert
```
POST /api/v1/send-alert
```
Manually send WhatsApp alert with latest prediction.

**Use Case:** Test notifications or send emergency alerts

---

#### 4. Farmer Registration
```
POST /api/v1/farmers/register
```
Register new farmers to receive alerts.

**Request Body:**
```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone_number": "+573001234567",
  "lot_address": "Finca Los Andes, Vereda Norte"
}
```

---

#### 5. Get All Farmers
```
GET /api/v1/farmers
```
List all registered farmers.

**Response:**
```json
{
  "farmers": [
    {
      "first_name": "Gabriela",
      "last_name": "Guevara",
      "phone_number": "+573012592676",
      "lot_address": "Finca La Esperanza",
      "registered_at": "2025-10-29T17:33:25Z"
    }
  ],
  "total": 1
}
```

---

#### 6. Health Check
```
GET /health
```
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "frost-prediction-api"
}
```

---

### User Experience

**For Farmers (Non-Technical Users):**

1. **Registration:** One-time registration with phone number
2. **Zero Interaction:** No app to install, no login required
3. **WhatsApp Alerts:** Receive messages on familiar platform
4. **Clear Guidance:** Simple risk levels with action items
5. **Personalized:** Messages addressed to them by name
6. **Spanish Language:** Accessible in local language

**Example Day in the Life:**

```
5:00 PM - Farmer's phone buzzes
WhatsApp message received:

"¡Hola! Gabriela Guevara

⚠️ *ADVERTENCIA DE HELADA* ⚠️

Posibles condiciones de helada esta noche.
Probabilidad: 63.7%

Monitoree las condiciones y esté preparado."

Action: Gabriela prepares frost protection equipment
```

---

## 12. Results & Impact

### System Performance

**Prediction Accuracy:**
- Hybrid model combines strengths of both approaches
- SARIMA captures temporal patterns
- LSTM captures multivariate relationships
- Daily average reduces false positives

**Operational Metrics:**
- **Predictions per day:** 3 (3 AM, 12 PM, 4 PM)
- **Alerts per day:** 1 (5 PM with daily average)
- **Model training time:**
  - SARIMA: 20-40 seconds
  - LSTM: 2-3 minutes
  - Cached predictions: <1 second
- **Alert delivery time:** <5 seconds via Twilio
- **System uptime:** 24/7 automated operation

---

### Benefits to Farmers

**Economic Impact:**
1. **Crop Loss Prevention**
   - Early warning enables protective measures
   - Reduces frost damage to sensitive crops
   - Protects farmer livelihood and income

2. **Cost Efficiency**
   - Free alert service (no subscription fees)
   - No hardware purchase required (uses existing sensors)
   - Operates via WhatsApp (no special app needed)

3. **Time Savings**
   - Automated alerts eliminate manual weather monitoring
   - Consolidated daily forecast (not constant updates)
   - Clear action guidance reduces decision time

**Risk Management:**
- **High confidence alerts (>70%):** Take immediate protective action
- **Medium confidence alerts (30-70%):** Stay prepared
- **Low confidence alerts (<30%):** Normal operations

---

### Scalability

**Current State:** 2 farmers, 1 sensor network
**Potential Scale:** Hundreds of farmers, multiple regions

**Scaling Strategy:**
1. **User Scale:**
   - Add farmers via API registration endpoint
   - Minimal cost increase (only Twilio WhatsApp messages)
   - Personalized alerts for each farmer

2. **Geographic Scale:**
   - Deploy additional LoRaWAN sensor networks
   - Multiple TTS application integrations
   - Region-specific prediction models

3. **Feature Scale:**
   - Add more crop-specific thresholds
   - Multi-language support (currently Spanish)
   - Historical analytics dashboard
   - Integration with other weather services

---

### Environmental & Social Impact

**Climate Resilience:**
- Helps farmers adapt to unpredictable weather patterns
- Supports sustainable agriculture practices
- Reduces need for excessive protective heating (energy conservation)

**Knowledge Transfer:**
- Demonstrates practical AI application in agriculture
- Accessible technology for rural communities
- Educational value for agricultural engineering

**Food Security:**
- Protects crop yields from frost damage
- Supports local food production
- Contributes to agricultural stability

---

## 13. Future Enhancements

### Short-Term Improvements (3-6 months)

#### 1. Enhanced Prediction Models
- **Ensemble Methods:** Add Random Forest, XGBoost models
- **Dynamic Weighting:** Adjust SARIMA/LSTM weights based on conditions
- **Longer Forecast:** Extend from 1-hour to 6-hour predictions
- **Confidence Intervals:** Provide prediction uncertainty ranges

#### 2. Additional Data Sources
- **Weather APIs:** Integrate external weather forecasts (OpenWeatherMap)
- **Soil Sensors:** Add soil temperature and moisture data
- **Satellite Data:** Incorporate cloud cover and radiation data
- **Multiple Sensors:** Support multiple sensor locations per farm

#### 3. User Interface
- **Web Dashboard:** Real-time predictions visualization
- **Historical Analytics:** View past predictions and accuracy
- **Farmer Portal:** Self-service registration and preferences
- **SMS Fallback:** For users without WhatsApp

---

### Medium-Term Enhancements (6-12 months)

#### 4. Crop-Specific Models
- **Crop Profiles:** Different thresholds for different crops
  - Coffee: Critical at <2°C
  - Strawberries: Critical at <-1°C
  - Flowers: Critical at <0°C
- **Phenological Stage:** Consider crop growth stage in risk assessment
- **Farm Customization:** Personalized models per farm microclimate

#### 5. Advanced Notifications
- **Multi-Channel:** SMS, Email, Push notifications, Voice calls
- **Severity Levels:** Differentiate between watch and warning
- **Action Recommendations:** Specific protective measures per crop
- **Follow-Up Alerts:** Updates if risk changes significantly

#### 6. Model Monitoring & Retraining
- **Prediction Tracking:** Log actual vs predicted frost events
- **Accuracy Metrics:** Calculate and display model performance
- **Automated Retraining:** Retrain models with new data monthly
- **A/B Testing:** Compare model versions in production

---

### Long-Term Vision (1-2 years)

#### 7. Regional Expansion
- **Multi-Region Support:** Deploy across multiple countries
- **Language Localization:** Spanish, English, Portuguese, French
- **Regional Models:** Train models specific to each climate zone
- **Farmer Networks:** Community sharing of best practices

#### 8. Advanced AI Capabilities
- **Explainable AI:** Visualize why model made specific prediction
- **Transfer Learning:** Apply knowledge from one region to another
- **Attention Mechanisms:** Identify which features most influence predictions
- **Generative AI:** Natural language explanations in alerts

#### 9. Integration Ecosystem
- **Government Weather Services:** Official forecast integration
- **Agricultural Insurance:** Automated claim support with prediction logs
- **Farm Management Systems:** Integration with existing agtech platforms
- **Research Institutions:** Data sharing for agricultural studies

#### 10. Mobile Application
- **Native Apps:** iOS and Android applications
- **Offline Mode:** View cached predictions without internet
- **Push Notifications:** Instant alerts without SMS/WhatsApp costs
- **Community Features:** Farmer-to-farmer communication

---

### Research Opportunities

**Academic Collaboration:**
- Publish results in agricultural engineering journals
- Collaborate with universities on model improvements
- Open-source components for research community

**Machine Learning Research:**
- Novel hybrid fusion techniques
- Transfer learning across different agricultural regions
- Explainability methods for agricultural AI

**Agricultural Research:**
- Correlation between predictions and actual crop damage
- Optimal protective measure timing based on predictions
- Cost-benefit analysis of AI-guided frost protection

---

## 14. Conclusion

### Key Achievements

This AI-powered frost prediction system demonstrates:

1. **Practical AI Application**
   - Real-world deployment in agricultural setting
   - Solves tangible problem for farmers
   - Accessible technology for rural communities

2. **Technical Excellence**
   - Clean Architecture for maintainability
   - Hybrid ML approach combining SARIMA and LSTM
   - Automated 24/7 operation with scheduling

3. **User-Centric Design**
   - WhatsApp alerts (familiar platform)
   - Spanish language (local language)
   - Clear risk levels with action guidance
   - Personalized messages

4. **Scalability & Extensibility**
   - Modular architecture supports expansion
   - Easy to add more farmers or regions
   - Foundation for future enhancements

---

### Impact Summary

**For Farmers:**
- Timely frost warnings enable protective actions
- Reduces crop damage and economic losses
- Free, accessible service via WhatsApp
- No technical expertise required

**For Agriculture:**
- Supports climate-resilient farming practices
- Protects food security and crop yields
- Demonstrates value of IoT + AI in agriculture
- Scalable to larger farming communities

**For Technology:**
- Practical demonstration of ML in production
- Hybrid model approach shows benefit of ensemble methods
- Clean Architecture principles in real-world application
- Open for research and academic collaboration

---

### Presentation Talking Points

**For International Congress:**

1. **Problem Framing:**
   "Frost causes millions in agricultural losses annually. Farmers need accurate, timely warnings to protect their livelihoods."

2. **Technical Innovation:**
   "Our hybrid ML system combines classical time series analysis (SARIMA) with deep learning (LSTM) for robust predictions."

3. **Real-World Impact:**
   "Currently serving farmers in Colombia with automated WhatsApp alerts. Zero technical barriers to adoption."

4. **Scalability:**
   "Architecture designed for expansion to hundreds of farmers and multiple regions. Modular design supports future enhancements."

5. **Accessibility:**
   "Uses familiar WhatsApp platform, Spanish language, and clear risk levels. Technology that serves, not intimidates."

6. **Research Value:**
   "Open to collaboration with agricultural engineering and AI researchers. Opportunities for model improvements and field studies."

---

### Call to Action

**For Researchers:**
- Collaborate on model improvements
- Access anonymized data for studies
- Contribute to open-source components

**For Farmers:**
- Register for free alerts
- Provide feedback on prediction accuracy
- Share with neighboring farmers

**For Investors/NGOs:**
- Support expansion to more regions
- Fund additional sensor deployments
- Partner for agricultural resilience programs

**For Engineers:**
- Contribute to codebase
- Propose architectural improvements
- Develop additional features

---

### Contact & Resources

**Project Repository:** (Add GitHub URL if open-sourced)

**Technical Documentation:** README.md

**API Documentation:** http://[your-domain]/docs (Swagger UI)

**System Architecture:** Clean Architecture with Onion layers

**Technologies:**
- Backend: FastAPI (Python)
- ML: TensorFlow (LSTM), Statsmodels (SARIMA)
- IoT: The Things Stack (LoRaWAN)
- Notifications: Twilio WhatsApp API
- Scheduling: APScheduler

---

## Appendix: Technical Glossary

**SARIMA:** Seasonal AutoRegressive Integrated Moving Average - Classical time series forecasting model

**LSTM:** Long Short-Term Memory - Type of recurrent neural network for sequential data

**LoRaWAN:** Long Range Wide Area Network - Low-power wireless protocol for IoT devices

**The Things Stack (TTS):** LoRaWAN network server for managing IoT sensor devices

**IoT:** Internet of Things - Network of physical devices with sensors and connectivity

**API:** Application Programming Interface - Software interface for communication between systems

**FastAPI:** Modern Python web framework for building APIs

**TensorFlow/Keras:** Open-source machine learning frameworks

**Clean Architecture:** Software design pattern with layered structure and dependency inversion

**Hybrid Model:** ML approach combining multiple models for improved accuracy

**Frost Probability:** Likelihood (0-100%) that frost conditions will occur

**Frost Level:** Risk classification (No Frost, Possible Frost, Frost Expected)

---

**END OF CONGRESS GUIDE**

---

*This document serves as a comprehensive reference for presenting the AI-powered frost prediction system at international congresses, academic conferences, or technical forums. It covers all aspects from problem statement to technical implementation to real-world impact.*

*Version: 1.0*
*Last Updated: October 31, 2025*
*Prepared for: International Congress Presentation*
