# Frost Prediction System

AI-powered frost prediction system that integrates with The Things Stack (TTS) for sensor data and uses machine learning models to predict frost conditions.

## Architecture

This project follows **Onion Architecture (Clean Architecture)** principles with clear separation of concerns:

```
├── domain/                     # Core business logic
│   ├── entities/              # Business entities
│   ├── value_objects/         # Value objects
│   ├── repositories/          # Repository interfaces
│   └── services/             # Domain service interfaces
├── application/               # Application logic
│   ├── use_cases/            # Use cases / interactors
│   ├── services/             # Application services
│   └── dtos/                 # Data transfer objects
├── infrastructure/           # External concerns
│   ├── repositories/         # Repository implementations
│   ├── external/             # External service clients
│   ├── models/               # ML model implementations
│   └── config/               # Configuration
└── interfaces/               # Presentation layer
    ├── controllers/          # FastAPI controllers
    ├── schemas/              # Request/response schemas
    └── middleware/           # HTTP middleware
```

## Features

- **Data Integration**: Connects to The Things Stack via webhook and Storage API
- **ML Models**: 
  - SARIMA(0,0,1)(0,1,2,144) for time series forecasting
  - LSTM neural network for multi-feature prediction
  - Hybrid fusion combining both models
- **Scheduling**: Automated predictions at 3:00am, 12:00pm, 4:00pm
- **Notifications**: WhatsApp alerts via Twilio at 5:00pm
- **Decision Rules**: 
  - \>70% probability → "Frost expected"
  - <30% probability → "No frost expected" 
  - Otherwise → "Possible frost alert"

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# The Things Stack
TTS_APPLICATION_ID=your_application_id
TTS_API_KEY=your_api_key
TTS_STORAGE_INTEGRATION_ID=your_storage_integration_id

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
RECIPIENT_WHATSAPP_NUMBER=your_phone_number
```

### 3. Run the Application

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Webhook Endpoint
```
POST /api/v1/webhook
```
Receives sensor data from The Things Stack.

### Manual Prediction
```
POST /api/v1/predict
```
Manually trigger a frost prediction.

### Send Alert
```
POST /api/v1/send-alert
```
Manually send the latest prediction via WhatsApp.

### Health Check
```
GET /health
```
Check API health status.

## Scheduler

The system automatically runs:
- **Prediction jobs**: 3:00am, 12:00pm, 4:00pm daily
- **Alert job**: 5:00pm daily (sends WhatsApp notification)

## ML Models

### SARIMA Model
- Uses last 10 days of temperature data
- Configuration: SARIMA(0,0,1)(0,1,2,144)
- 144 = seasonal period (24 hours × 6 intervals per hour)

### LSTM Model
- Uses temperature, humidity, and wind speed
- Sequence length: 144 intervals (12 hours)
- Architecture: 2 LSTM layers with dropout

### Hybrid Fusion
- Combines SARIMA and LSTM predictions
- Weighted average (LSTM 60%, SARIMA 40%)
- Provides final frost probability

## Development

### Project Structure
The project follows clean architecture principles with dependency inversion. Each layer only depends on inner layers, ensuring high modularity and testability.

### Adding New Features
1. Add domain entities/interfaces in `domain/`
2. Implement use cases in `application/`
3. Add infrastructure implementations in `infrastructure/`
4. Expose via controllers in `interfaces/`

## Monitoring

Logs are printed to console showing:
- Webhook receptions
- Prediction job execution
- Alert sending status
- API request/response times

## Production Deployment

For production deployment:
1. Set `DEBUG=False` in environment
2. Use production-grade ASGI server
3. Add proper logging configuration
4. Implement health monitoring
5. Set up SSL/TLS termination