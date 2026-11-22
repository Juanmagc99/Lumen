"""Safe operational logging shared by backend processes."""

import json
import logging
import os
import re
from datetime import datetime, timezone

_OPERATIONS = {"http_request", "classification", "ingestion", "semantic_index", "generation"}
_EVENTS = {
    "request_failed": {"request_id", "operation"},
    "worker_operation_failed": {"operation"},
    "worker_started": {"operation"},
    "classification_attempt_failed": {"operation"},
    "http_access": {"request_id", "method", "route", "status", "duration_ms"},
    "server_event": set(),
}
_STANDARD = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}
_ROUTES: set[str] = {"unmatched"}
_ACCESS_HANDLER = None


def set_safe_routes(routes) -> None:
    _ROUTES.clear()
    _ROUTES.add("unmatched")
    _ROUTES.update(route for route in routes if isinstance(route, str))


def _valid(field, value):
    if field == "operation":
        return value in _OPERATIONS if isinstance(value, str) else False
    if field == "request_id":
        return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{32}", value))
    if field == "method":
        return value in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "OTHER"}
    if field == "route":
        return isinstance(value, str) and value in _ROUTES
    if field == "status":
        return type(value) is int and 100 <= value <= 599
    if field == "duration_ms":
        return type(value) in (int, float) and 0 <= value < 1e12
    return False


class SafeEventHandler(logging.StreamHandler):
    def __init__(self, service: str):
        super().__init__()
        self.service = service

    def _write(self, severity, event, fields):
        payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "severity": severity, "service": self.service, "event": event, **fields}
        self.stream.write(json.dumps(payload, ensure_ascii=True) + self.terminator)
        self.flush()

    def emit(self, record):
        # Never format messages, arguments, exception text or tracebacks from callers.
        try:
            event = record.msg if isinstance(record.msg, str) and not record.args else None
            rejected = event not in _EVENTS or bool(record.exc_info or record.stack_info)
            if event in _EVENTS:
                fields = {}
                extras = set(record.__dict__) - _STANDARD
                for field in extras:
                    value = record.__dict__[field]
                    if field in _EVENTS[event] and _valid(field, value):
                        fields[field] = value
                    else:
                        rejected = True
                self._write(record.levelname if record.levelname in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"} else "ERROR", event, fields)
            if rejected:
                self._write("WARNING", "logging_value_rejected", {})
        except Exception:
            # Logging must never interrupt application work or recursively log errors.
            pass


class ServerEventHandler(SafeEventHandler):
    def emit(self, record):
        try:
            severity = record.levelname if record.levelname in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"} else "ERROR"
            self._write(severity, "server_event", {})
        except Exception:
            pass


def log_access(method, route, status, duration_ms, request_id):
    if _ACCESS_HANDLER is None:
        return
    record = logging.LogRecord("lumen.access", logging.INFO, "", 0, "http_access", (), None)
    record.method = method if method in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"} else "OTHER"
    record.route = route if route in _ROUTES else "unmatched"
    record.status, record.duration_ms, record.request_id = status, duration_ms, request_id
    _ACCESS_HANDLER.handle(record)


def configure_logging(service: str) -> None:
    global _ACCESS_HANDLER
    level = os.environ.get("LUMEN_LOG_LEVEL", "INFO").upper()
    if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("LUMEN_LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL.")
    handler = SafeEventHandler(service)
    logger = logging.getLogger("lumen")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    logging.getLogger().setLevel(logging.WARNING)
    if service == "api":
        _ACCESS_HANDLER = SafeEventHandler(service)
        server = logging.getLogger("uvicorn")
        server.handlers.clear()
        server.addHandler(ServerEventHandler(service))
        server.setLevel(level)
        server.propagate = False
        server_error = logging.getLogger("uvicorn.error")
        server_error.handlers.clear()
        server_error.setLevel(level)
        server_error.propagate = True
        access = logging.getLogger("uvicorn.access")
        access.handlers.clear()
        access.propagate = False
        access.disabled = True
