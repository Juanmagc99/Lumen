"""Stable, safe failure categories shared by HTTP and background jobs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorDefinition:
    message: str
    status: int | None = None


ERRORS = {
    "BAD_REQUEST": ErrorDefinition("The request is invalid.", 400),
    "UNAUTHENTICATED": ErrorDefinition("Sign in required.", 401),
    "FORBIDDEN": ErrorDefinition("Access denied.", 403),
    "NOT_FOUND": ErrorDefinition("The requested resource was not found.", 404),
    "METHOD_NOT_ALLOWED": ErrorDefinition("The request method is not allowed.", 405),
    "CONFLICT": ErrorDefinition("The request conflicts with the current state.", 409),
    "STALE_REVISION": ErrorDefinition("The saved version changed. Reload before trying again.", 409),
    "CONTENT_TOO_LARGE": ErrorDefinition("Content exceeds the configured size limit.", 413),
    "UNSUPPORTED_MEDIA": ErrorDefinition("The request content type is not supported.", 415),
    "INVALID_INPUT": ErrorDefinition("The request contains invalid input.", 422),
    "QUEUE_FULL": ErrorDefinition("The generation queue is full. Try again later.", 429),
    "RATE_LIMITED": ErrorDefinition("Too many requests. Try again later.", 429),
    "INTERNAL_ERROR": ErrorDefinition("An unexpected error occurred.", 500),
    "STORAGE_UNAVAILABLE": ErrorDefinition("Storage is unavailable. Try again later.", 503),
    "JOB_FAILED": ErrorDefinition("The job failed."),
    "MODEL_CONFIGURATION": ErrorDefinition("The model configuration is unavailable."),
    "MODEL_PROVIDER": ErrorDefinition("The model provider is unavailable."),
    "INVALID_MODEL_OUTPUT": ErrorDefinition("The model returned an invalid result."),
    "NO_OPTIONS": ErrorDefinition("Classification options are unavailable."),
    "INGESTION_FAILED": ErrorDefinition("Document processing failed."),
    "INDEXING_FAILED": ErrorDefinition("Semantic indexing unavailable."),
    "ATTEMPTS_EXHAUSTED": ErrorDefinition("Processing attempts exhausted."),
    "CLAIM_EXPIRED": ErrorDefinition("The processing claim expired."),
}

# Context disambiguates identical legacy values from different job types.
LEGACY_FAILURES = {
    "classification": {"configuration": "MODEL_CONFIGURATION", "provider": "MODEL_PROVIDER", "invalid_decision": "INVALID_MODEL_OUTPUT", "no_options": "NO_OPTIONS"},
    "generation": {"configuration": "MODEL_CONFIGURATION", "provider": "MODEL_PROVIDER", "invalid_output": "INVALID_MODEL_OUTPUT", "attempts_exhausted": "ATTEMPTS_EXHAUSTED", "claim_expired": "CLAIM_EXPIRED"},
    "ingestion": {"Processing attempts exhausted.": "ATTEMPTS_EXHAUSTED", "Document processing failed.": "INGESTION_FAILED"},
    "indexing": {"Indexing attempts exhausted.": "ATTEMPTS_EXHAUSTED", "Semantic indexing unavailable.": "INDEXING_FAILED"},
}

HTTP_STATUS_CODES = {
    400: "BAD_REQUEST", 401: "UNAUTHENTICATED", 403: "FORBIDDEN",
    404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED", 409: "CONFLICT",
    413: "CONTENT_TOO_LARGE", 415: "UNSUPPORTED_MEDIA", 422: "INVALID_INPUT",
    429: "RATE_LIMITED", 500: "INTERNAL_ERROR", 503: "STORAGE_UNAVAILABLE",
}


def failure_code(kind: str, value: str | None) -> str | None:
    """Map a stored or known legacy failure without exposing unknown values."""
    if value is None:
        return None
    if value in ERRORS and ERRORS[value].status is None:
        return value
    return LEGACY_FAILURES.get(kind, {}).get(value, "JOB_FAILED")


def failure_message(kind: str, value: str | None) -> str | None:
    code = failure_code(kind, value)
    return ERRORS[code].message if code else None
