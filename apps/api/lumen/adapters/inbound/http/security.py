"""Fail-closed HTTP security boundary for the shared workspace."""

import os
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from fastapi import Request
from lumen.adapters.inbound.http.errors import error_response

from lumen.adapters.inbound.http.authentication import COOKIE_NAME
from lumen.domain.tickets import StorageUnavailable

_ID = r"[0-9a-fA-F-]{36}"
_POLICY = [
    ("GET", r"/api/auth/session", "operator"),
    ("POST", r"/api/auth/(logout|password)", "operator"),
    ("GET", r"/api/auth/users", "administrator"),
    ("POST", r"/api/auth/users", "administrator"),
    ("PATCH", rf"/api/auth/users/{_ID}", "administrator"),
    ("GET", r"/api/classification-options", "operator"),
    ("POST", r"/api/classification-options", "administrator"),
    ("PATCH", rf"/api/classification-options/{_ID}", "administrator"),
    ("GET", r"/api/tickets", "operator"),
    ("POST", r"/api/tickets", "operator"),
    ("GET", rf"/api/tickets/{_ID}", "operator"),
    ("POST", rf"/api/tickets/{_ID}/classification/retry", "operator"),
    ("PATCH", rf"/api/tickets/{_ID}/classification", "operator"),
    ("GET", rf"/api/tickets/{_ID}/response", "operator"),
    ("PUT", rf"/api/tickets/{_ID}/response", "operator"),
    ("POST", rf"/api/tickets/{_ID}/response/approval", "operator"),
    ("GET", rf"/api/tickets/{_ID}/generations", "operator"),
    ("POST", rf"/api/tickets/{_ID}/generations", "operator"),
    ("GET", r"/api/knowledge/bases", "operator"),
    ("POST", r"/api/knowledge/bases", "operator"),
    ("GET", rf"/api/knowledge/bases/{_ID}/documents", "operator"),
    ("POST", rf"/api/knowledge/bases/{_ID}/documents", "operator"),
    ("POST", rf"/api/knowledge/documents/{_ID}/versions", "operator"),
    ("PATCH", rf"/api/knowledge/documents/{_ID}", "operator"),
    ("GET", rf"/api/knowledge/versions/{_ID}", "operator"),
    ("POST", rf"/api/knowledge/versions/{_ID}/retry", "operator"),
    ("POST", rf"/api/knowledge/versions/{_ID}/semantic-retry", "operator"),
]


@dataclass(frozen=True)
class SecuritySettings:
    origin: str
    secure_cookie: bool

    @classmethod
    def from_environment(cls):
        local = os.environ.get("LUMEN_LOCAL_AUTH", "false").lower() == "true"
        origin = os.environ.get("LUMEN_PUBLIC_ORIGIN", "")
        parsed = urlsplit(origin)
        if not origin or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment or parsed.scheme not in ("http", "https"):
            raise RuntimeError("LUMEN_PUBLIC_ORIGIN must be an HTTP(S) origin without a path.")
        if local:
            if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
                raise RuntimeError("Local authentication requires an HTTP loopback origin.")
        elif parsed.scheme != "https":
            raise RuntimeError("HTTPS is required outside local authentication mode.")
        return cls(origin=origin, secure_cookie=not local)


def same_origin(request: Request, expected: str) -> bool:
    origin = request.headers.get("origin")
    if origin is not None:
        return origin == expected
    referer = request.headers.get("referer")
    if not referer:
        return False
    parsed = urlsplit(referer)
    return f"{parsed.scheme}://{parsed.netloc}" == expected and not parsed.username and not parsed.password


def install_security(app, auth, settings: SecuritySettings):
    @app.middleware("http")
    async def security_boundary(request: Request, call_next):
        path, method = request.url.path, request.method
        if path == "/health" and method == "GET":
            request.state.routing_allowed = True
            return await call_next(request)
        if path == "/api/auth/login" and method == "POST":
            if not same_origin(request, settings.origin):
                return error_response(request, "FORBIDDEN")
            if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
                return error_response(request, "UNSUPPORTED_MEDIA")
            request.state.routing_allowed = True
            return await call_next(request)
        token = request.cookies.get(COOKIE_NAME)
        try:
            user = await auth.current(token) if token else None
        except StorageUnavailable:
            return error_response(request, "STORAGE_UNAVAILABLE")
        if user is None:
            return error_response(request, "UNAUTHENTICATED")
        if method not in ("GET", "HEAD", "OPTIONS") and not same_origin(request, settings.origin):
            return error_response(request, "FORBIDDEN")
        if method in ("POST", "PATCH") and (path == "/api/auth/password" or path.startswith("/api/auth/users")) and request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
            return error_response(request, "UNSUPPORTED_MEDIA")
        required = next((role for allowed_method, pattern, role in _POLICY if method == allowed_method and re.fullmatch(pattern, path)), None)
        if required is None:
            return error_response(request, "FORBIDDEN")
        if required == "administrator" and user.role != "administrator":
            return error_response(request, "FORBIDDEN")
        request.state.routing_allowed = True
        return await call_next(request)
