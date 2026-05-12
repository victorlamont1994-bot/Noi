from fastapi import Header, HTTPException
from backend.config import settings


def require_rose_key(x_rose_api_key: str | None = Header(default=None)):
    if not settings.require_api_key:
        return True

    if not settings.rose_api_key or settings.rose_api_key == "change-me-before-network-use":
        raise HTTPException(
            status_code=500,
            detail="API-key enforcement is enabled but ROSE_API_KEY is not configured.",
        )

    if x_rose_api_key != settings.rose_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized: invalid or missing ROSE API key.")

    return True
