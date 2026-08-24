from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidFileException(AppException):
    """Raised when an uploaded file is invalid (unsupported type, empty, corrupt)."""

    def __init__(self, message: str = "Only PDF files are supported."):
        super().__init__(
            code="INVALID_FILE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class FileNotFoundException(AppException):
    """Raised when a requested document is not found."""

    def __init__(self, message: str = "The requested document was not found."):
        super().__init__(
            code="DOCUMENT_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class FileTooLargeException(AppException):
    """Raised when an uploaded file exceeds the configured size limit."""

    def __init__(self, message: str = "The uploaded file exceeds the maximum allowed size."):
        super().__init__(
            code="FILE_TOO_LARGE",
            message=message,
            status_code=status.HTTP_413_CONTENT_TOO_LARGE
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for custom application domain exceptions."""
    logger.warning(f"Domain exception on {request.url.path}: [{exc.code}] {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for standard FastAPI/Starlette HTTPExceptions."""
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        413: "PAYLOAD_TOO_LARGE",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR"
    }
    code = code_map.get(exc.status_code, "ERROR")
    message = str(exc.detail) if exc.detail else "An HTTP error occurred."
    logger.warning(f"HTTP exception on {request.url.path}: [{code}] {message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for Pydantic validation errors."""
    errors = exc.errors()
    # Extract the first error message for clear output
    first_msg = errors[0].get("msg", "Validation error") if errors else "Invalid request body."
    field_loc = " -> ".join([str(loc) for loc in errors[0].get("loc", [])]) if errors else ""
    full_msg = f"{first_msg} ({field_loc})" if field_loc else first_msg
    logger.warning(f"Validation error on {request.url.path}: {full_msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": full_msg
            }
        }
    )



async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled internal exceptions."""
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred."
            }
        }
    )
