import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from dependencies import dependencies
from scheduler import FrostPredictionScheduler
from interfaces.middleware.logging_middleware import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[STARTUP] Initializing application...")

    # Try to pre-initialize database (don't block if it fails)
    try:
        print("[STARTUP] Pre-warming database connection...")
        dependencies.sensor_database._initialize_database()
    except Exception as e:
        print(f"[STARTUP] Database pre-warm skipped: {e}")

    scheduler = FrostPredictionScheduler(
        dependencies.prediction_service,
        dependencies.sensor_data_service
    )
    scheduler.start()
    print("[STARTUP] Application ready!")

    yield

    # Shutdown
    scheduler.stop()


app = FastAPI(
    title="Frost Prediction System",
    description="AI-powered frost prediction system using TTS sensors and ML models",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(dependencies.webhook_controller.router, prefix="/api/v1", tags=["webhooks"])
app.include_router(dependencies.prediction_controller.router, prefix="/api/v1", tags=["predictions"])
app.include_router(dependencies.farmer_controller.router, prefix="/api/v1", tags=["farmers"])


@app.get("/")
async def root():
    return {"message": "Frost Prediction System API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "frost-prediction-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)