"""Custom exception handlers for consistent API error responses."""

import uuid
import logging
from typing import Any, Dict, Optional, List, Union

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response model."""
    success: bool = False
    message: str
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    request_id: Optional[str] = None
    status_code: int = 500


def get_request_id(request: Request) -> str:
    """Get or generate a request ID for tracing."""
    req_id = request.headers.get("X-Request-ID")
    if not req_id:
        req_id = str(uuid.uuid4())[:8]
    return req_id


def create_error_response(
    request: Request,
    message: str,
    status_code: int,
    errors: Optional[List[Dict[str, Any]]] = None,
) -> JSONResponse:
    """Create a standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            message=message,
            errors=errors or [],
            request_id=get_request_id(request),
            status_code=status_code,
        ).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with consistent format."""
    logger.warning(
        "HTTP %s: %s - %s %s",
        exc.status_code,
        exc.detail,
        request.method,
        request.url.path,
    )
    return create_error_response(
        request=request,
        message=str(exc.detail),
        status_code=exc.status_code,
        errors=[{"detail": str(exc.detail)}] if exc.detail else None,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with detailed field errors."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Validation error")
        errors.append({"field": field, "message": msg, "type": error.get("type")})

    logger.warning(
        "Validation error: %s - %s %s",
        errors,
        request.method,
        request.url.path,
    )

    return create_error_response(
        request=request,
        message="Validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors,
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions - never expose stack traces."""
    from app.core.config import settings
    request_id = get_request_id(request)
    logger.exception(
        "Unhandled exception [req=%s] %s %s: %s",
        request_id,
        request.method,
        request.url.path,
        str(exc),
    )

    return create_error_response(
        request=request,
        message="An internal error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors=[{"request_id": request_id}] if not settings.is_production else None,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Exception handlers registered")