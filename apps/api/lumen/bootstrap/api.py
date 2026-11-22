"""Compose the HTTP application and its persistence adapter."""

import os
import logging
import re
from time import monotonic
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from lumen.adapters.inbound.http.routes import router_for
from lumen.adapters.inbound.http.knowledge import router_for_knowledge
from lumen.adapters.inbound.http.generations import router_for_generations
from lumen.adapters.inbound.http.authentication import router_for_authentication
from lumen.adapters.inbound.http.security import SecuritySettings, install_security
from lumen.adapters.inbound.http.errors import error_response, http_error_response
from lumen.adapters.outbound.db.accounts import PostgresAccounts
from lumen.adapters.outbound.db.authentication import PostgresAuthentication
from lumen.adapters.outbound.db.knowledge import PostgresKnowledge
from lumen.adapters.outbound.db.response_generations import PostgresResponseGenerations
from lumen.adapters.outbound.db.tickets import PostgresTickets
from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.application.tickets import Tickets
from lumen.application.knowledge import Knowledge
from lumen.bootstrap.config import database_url, _positive_int, GenerationSettings
from lumen.bootstrap.observability import configure_logging, log_access, set_safe_routes
from lumen.domain.tickets import StorageUnavailable

configure_logging("api")
app = FastAPI(title="Lumen API")
security_settings = SecuritySettings.from_environment()
account_sessions = DatabaseSessions(database_url)
authentication = PostgresAuthentication(account_sessions, _positive_int(os.environ.get("LUMEN_SIGNIN_FAILURE_LIMIT", "5"), "LUMEN_SIGNIN_FAILURE_LIMIT"))
app.include_router(router_for_authentication(authentication, PostgresAccounts(account_sessions), security_settings.secure_cookie))
install_security(app, authentication, security_settings)


@app.middleware("http")
async def error_boundary(request: Request, call_next):
    request_id = uuid4().hex
    request.state.request_id = request_id
    started = monotonic()
    try:
        response = await call_next(request)
    except Exception as exc:
        logging.getLogger("lumen.api").error(
            "request_failed",
            extra={"request_id": request_id, "operation": "http_request"},
        )
        response = error_response(request, "INTERNAL_ERROR")
    response.headers["X-Request-ID"] = request_id
    try:
        route = "unmatched"
        if getattr(request.state, "routing_allowed", False):
            for template, methods in app.openapi()["paths"].items():
                pattern = re.sub(r"\\\{[^{}]+\\\}", r"[^/]+", re.escape(template))
                if request.method.lower() in methods and re.fullmatch(pattern, request.url.path):
                    route = template
                    break
        log_access(request.method, route, response.status_code, (monotonic() - started) * 1000, request_id)
    except Exception:
        pass
    return response


app.include_router(router_for(Tickets(PostgresTickets(DatabaseSessions(database_url)))))
app.include_router(router_for_knowledge(Knowledge(PostgresKnowledge(DatabaseSessions(database_url), lambda: (os.environ.get("LUMEN_EMBEDDING_MODEL") or "text-embedding-3-small", _positive_int(os.environ.get("LUMEN_EMBEDDING_DIMENSIONS", "1536"), "LUMEN_EMBEDDING_DIMENSIONS", 16000))), max_bytes=_positive_int(os.environ.get("LUMEN_KNOWLEDGE_MAX_BYTES", "1048576"), "LUMEN_KNOWLEDGE_MAX_BYTES"))))
app.include_router(router_for_generations(PostgresResponseGenerations(DatabaseSessions(database_url), GenerationSettings.from_environment())))
set_safe_routes(app.openapi()["paths"])


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return error_response(request, "INVALID_INPUT")


@app.exception_handler(StorageUnavailable)
async def storage_unavailable(request: Request, __: StorageUnavailable):
    return error_response(request, "STORAGE_UNAVAILABLE")


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return http_error_response(request, exc)
