"""Fixed bearer token authentication."""

from __future__ import annotations

from hmac import compare_digest

from fastapi import Header, Request

from .openai_compat.errors import GatewayError


def require_api_key(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> None:
    settings = request.app.state.settings
    if not settings.api_key:
        raise GatewayError(
            status_code=500,
            message="The gateway API key is not configured.",
            code="api_key_not_configured",
            error_type="server_error",
        )

    if authorization is None:
        raise GatewayError(
            status_code=401,
            message="Missing bearer token.",
            code="missing_api_key",
            error_type="authentication_error",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise GatewayError(
            status_code=401,
            message="Invalid authorization header.",
            code="invalid_authorization_header",
            error_type="authentication_error",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not compare_digest(parts[1], settings.api_key):
        raise GatewayError(
            status_code=401,
            message="Invalid API key.",
            code="invalid_api_key",
            error_type="authentication_error",
            headers={"WWW-Authenticate": "Bearer"},
        )
