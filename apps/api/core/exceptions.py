"""Application-level exceptions and HTTP error handlers."""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class StormnetException(Exception):
    """Base exception class for STORMNET domain errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundException(StormnetException):
    """Raised when a requested domain entity is not found."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class SpatialQueryException(StormnetException):
    """Raised when a PostGIS spatial query fails or produces invalid geometry."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class DataIngestionException(StormnetException):
    """Raised when a raw radar or satellite stream fails validation."""

    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"Ingestion failed for provider '{provider}': {reason}",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers on the FastAPI application."""

    @app.exception_handler(StormnetException)
    async def stormnet_exception_handler(request: Request, exc: StormnetException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                    "path": str(request.url),
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected server error occurred.",
                    "details": str(exc) if app.debug else {},
                    "path": str(request.url),
                }
            },
        )
