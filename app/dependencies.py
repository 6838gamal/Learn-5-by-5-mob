"""FastAPI dependencies shared across routers."""

from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from app.services.api_client import ApiClient
from app.config import get_settings


settings = get_settings()


def get_api_client(request: Request) -> ApiClient:
    """Return an ApiClient pre-configured with the current user's token (if any)."""
    token = request.session.get("access_token")
    return ApiClient(base_url=settings.API_BASE_URL, access_token=token)


def require_auth(request: Request):
    """Redirect to /auth/login if not authenticated."""
    if not request.session.get("access_token"):
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/auth/login"},
        )
