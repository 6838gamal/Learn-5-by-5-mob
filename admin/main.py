"""Standalone entry point for the Admin dashboard service."""
import uvicorn
from admin.app import admin_app  # noqa: F401 — imported for side-effects (routes registered)

# Re-export as `app` so uvicorn can find it via `admin.main:app`
app = admin_app

if __name__ == "__main__":
    uvicorn.run("admin.main:app", host="0.0.0.0", port=8001, reload=False)
