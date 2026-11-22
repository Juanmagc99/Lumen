"""HTTP adapter for application-owned safe errors."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from lumen.domain.errors import ERRORS, HTTP_STATUS_CODES


class CatalogueHTTPException(HTTPException):
    def __init__(self, code: str):
        self.code = code
        definition = ERRORS[code]
        super().__init__(status_code=definition.status, detail=definition.message)


def error_response(request: Request, code: str, status: int | None = None, headers=None):
    definition = ERRORS[code]
    request_id = request.state.request_id
    return JSONResponse(
        status_code=status or definition.status,
        content={"error": {"code": code, "message": definition.message, "request_id": request_id}},
        headers={**(headers or {}), "X-Request-ID": request_id},
    )


def http_error_response(request: Request, exc: HTTPException):
    code = getattr(exc, "code", None) or HTTP_STATUS_CODES.get(exc.status_code, "INTERNAL_ERROR")
    return error_response(request, code, exc.status_code, exc.headers)
