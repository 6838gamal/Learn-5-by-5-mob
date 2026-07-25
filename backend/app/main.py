from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.api.v1.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # API routes
    app.include_router(api_router, prefix="/api/v1")

    # Admin dashboard (lives at /admin in the workspace root)
    from admin.app import admin_app
    app.mount("/admin", admin_app)

    # Static files (uploads)
    import os
    os.makedirs("static/uploads", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
