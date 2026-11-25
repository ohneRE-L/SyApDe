"""
Единая точка преобразования доменных ошибок и ошибок валидации в HTTP-статусы.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from internal.domain.errors import (
    ConflictError,
    DatabaseError,
    InvalidInputError,
    NotFoundError,
)

logger = logging.getLogger("helpdesk.errors")


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует обработчики исключений на уровне приложения FastAPI."""

    @app.exception_handler(InvalidInputError)
    async def invalid_input_handler(_request: Request, exc: InvalidInputError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Validation error: {exc.errors()}"},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": str(exc)})

    @app.exception_handler(ConflictError)
    async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"error": str(exc)})

    @app.exception_handler(DatabaseError)
    async def database_error_handler(_request: Request, exc: DatabaseError) -> JSONResponse:
        logger.error("Database error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal database error"},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"},
        )
