from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    def __init__(self, message: str, code: str = "ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", code="NOT_FOUND", status_code=404)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, code="UNAUTHORIZED", status_code=401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, code="FORBIDDEN", status_code=403)


class ConflictError(AppException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, code="CONFLICT", status_code=409)


class SubscriptionRequiredError(AppException):
    def __init__(self, feature: str = "this feature"):
        super().__init__(
            f"A Premium subscription is required to access {feature}.",
            code="SUBSCRIPTION_REQUIRED",
            status_code=402,
        )


def _error_response(status_code: int, message: str, code: str = "ERROR", details=None):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "data": None, "message": message, "code": code, "details": details},
    )


async def app_exception_handler(request: Request, exc: AppException):
    return _error_response(exc.status_code, exc.message, exc.code)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Validation error",
        "VALIDATION_ERROR",
        details=exc.errors(),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return _error_response(500, "Internal server error", "INTERNAL_ERROR")
