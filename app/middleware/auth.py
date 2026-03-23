from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
import hashlib
import hmac

EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}

VALID_API_KEYS: set[str] = set(
    filter(None, os.getenv("API_KEYS", "dev-key-12345,test-key-67890").split(","))
)


def verify_api_key(key: str) -> bool:
    return any(
        hmac.compare_digest(key.strip(), valid_key.strip())
        for valid_key in VALID_API_KEYS
    )


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        api_key = (
            request.headers.get("X-API-Key")
            or request.headers.get("Authorization", "").removeprefix("Bearer ")
        )

        if not api_key or not verify_api_key(api_key):
            return JSONResponse(
                status_code=401,
                content={
                    "error": "unauthorized",
                    "message": "Missing or invalid API key. Pass X-API-Key header.",
                },
            )

        request.state.api_key = api_key[:8] + "..."
        return await call_next(request)
