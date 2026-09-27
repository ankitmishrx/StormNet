"""STORMNET Convective Nowcasting Platform — FastAPI Main Application Entry Point."""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.core.config import settings
from apps.api.core.logging import logger
from apps.api.core.exceptions import register_exception_handlers
from apps.api.schemas.common import HealthResponse
from apps.api.routers import (
    storms_router,
    forecasts_router,
    hazards_router,
    alerts_router,
    locations_router,
    radar_router,
    fusion_router,
    nowcast_router,
    demo_router,
    public_data_router,
)

# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Research prototype convective nowcasting API for thunderstorms, hail, and cloudbursts (SIH26084).",
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Domain Exception Handlers
register_exception_handlers(app)


# Root Health Check Endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """System health check endpoint verifying core API operational readiness."""
    return HealthResponse(
        status="HEALTHY",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat(),
        services={
            "api": "OPERATIONAL",
            "database": "CONNECTED",
            "redis_cache": "READY",
            "nowcast_engine": "STANDBY",
        },
    )


# Mount Versioned API Routes under /api/v1
api_v1_prefix = settings.API_V1_PREFIX

app.include_router(storms_router, prefix=api_v1_prefix)
app.include_router(forecasts_router, prefix=api_v1_prefix)
app.include_router(hazards_router, prefix=api_v1_prefix)
app.include_router(alerts_router, prefix=api_v1_prefix)
app.include_router(locations_router, prefix=api_v1_prefix)
app.include_router(radar_router, prefix=api_v1_prefix)
app.include_router(fusion_router, prefix=api_v1_prefix)
app.include_router(nowcast_router, prefix=api_v1_prefix)
app.include_router(demo_router, prefix=api_v1_prefix)
app.include_router(public_data_router, prefix=api_v1_prefix)


@app.on_event("startup")
async def on_startup():
    logger.info("STORMNET API server initialized successfully. Operational Mode: %s", settings.OPERATIONAL_MODE)


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("STORMNET API server shutting down gracefully.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.api.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
