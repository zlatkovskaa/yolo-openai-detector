"""OpenAI-like error helpers."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request
from fastapi.responses import JSONResponse


@dataclass(slots=True)
class GatewayError(Exception):
    """Application error that should be serialized as an API response."""

    status_code: int
    message: str
    code: str
    error_type: str = "invalid_request_error"
    param: str | None = None
    headers: dict[str, str] | None = None

    def __post_init__(self) -> None:
        Exception.__init__(self, self.message)

    def payload(self) -> dict[str, object]:
        error: dict[str, object] = {
            "message": self.message,
            "type": self.error_type,
            "code": self.code,
        }
        if self.param is not None:
            error["param"] = self.param
        return {"error": error}


async def gateway_error_handler(_: Request, exc: GatewayError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.payload(),
        headers=exc.headers,
    )
