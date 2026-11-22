"""Compose the HTTP application and its persistence adapter."""

import os

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from lumen.adapters.inbound.http.routes import router_for
from lumen.adapters.inbound.http.knowledge import router_for_knowledge
from lumen.adapters.inbound.http.generations import router_for_generations
from lumen.adapters.inbound.http.authentication import router_for_authentication
from lumen.adapters.inbound.http.security import SecuritySettings, install_security
from lumen.adapters.outbound.db.accounts import PostgresAccounts
from lumen.adapters.outbound.db.authentication import PostgresAuthentication
from lumen.adapters.outbound.db.knowledge import PostgresKnowledge
from lumen.adapters.outbound.db.response_generations import PostgresResponseGenerations
from lumen.adapters.outbound.db.tickets import PostgresTickets
from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.application.tickets import Tickets
from lumen.application.knowledge import Knowledge
from lumen.bootstrap.config import database_url, _positive_int, GenerationSettings
from lumen.domain.tickets import StorageUnavailable

app = FastAPI(title="Lumen API")
security_settings = SecuritySettings.from_environment()
account_sessions = DatabaseSessions(database_url)
authentication = PostgresAuthentication(account_sessions, _positive_int(os.environ.get("LUMEN_SIGNIN_FAILURE_LIMIT", "5"), "LUMEN_SIGNIN_FAILURE_LIMIT"))
app.include_router(router_for_authentication(authentication, PostgresAccounts(account_sessions), security_settings.secure_cookie))
install_security(app, authentication, security_settings)
app.include_router(router_for(Tickets(PostgresTickets(DatabaseSessions(database_url)))))
app.include_router(router_for_knowledge(Knowledge(PostgresKnowledge(DatabaseSessions(database_url), lambda: (os.environ.get("LUMEN_EMBEDDING_MODEL") or "text-embedding-3-small", _positive_int(os.environ.get("LUMEN_EMBEDDING_DIMENSIONS", "1536"), "LUMEN_EMBEDDING_DIMENSIONS", 16000))), max_bytes=_positive_int(os.environ.get("LUMEN_KNOWLEDGE_MAX_BYTES", "1048576"), "LUMEN_KNOWLEDGE_MAX_BYTES"))))
app.include_router(router_for_generations(PostgresResponseGenerations(DatabaseSessions(database_url), GenerationSettings.from_environment())))


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api/auth/"):
        return JSONResponse(status_code=422, content={"detail": "Invalid account or session request."})
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(StorageUnavailable)
async def storage_unavailable(_: Request, __: StorageUnavailable):
    return JSONResponse(status_code=503, content={"detail": "Storage is unavailable. Try again later."})
