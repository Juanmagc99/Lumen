"""Typed process settings read from the environment.

Development tooling loads the root .env file before starting processes.
"""

import os
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field
from typing import Mapping

from sqlalchemy.engine import URL


def _positive_int(value: str, name: str, maximum: int | None = None) -> int:
    try:
        parsed = int(value)
    except ValueError:
        parsed = 0
    if parsed < 1 or (maximum is not None and parsed > maximum):
        requirement = f"an integer between 1 and {maximum}" if maximum is not None else "a positive integer"
        raise ValueError(f"{name} must be {requirement}") from None
    return parsed


@dataclass(frozen=True)
class DatabaseSettings:
    url: str = field(repr=False)

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "DatabaseSettings":
        env = os.environ if environment is None else environment
        url = env.get("DATABASE_URL")
        if url:
            return cls(url=url)
        user = env.get("LUMEN_POSTGRES_USER")
        password = env.get("LUMEN_POSTGRES_PASSWORD")
        database = env.get("LUMEN_POSTGRES_DB")
        if not all((user, password, database)):
            raise RuntimeError("Database user, password, and name are required")
        try:
            port = _positive_int(env.get("LUMEN_POSTGRES_PORT") or "5432", "LUMEN_POSTGRES_PORT", 65535)
        except ValueError as exc:
            raise RuntimeError(str(exc)) from None
        url = URL.create("postgresql+asyncpg", username=user, password=password, host="127.0.0.1", port=port, database=database)
        return cls(url=url.render_as_string(hide_password=False))


def database_url() -> str:
    return DatabaseSettings.from_environment().url


@dataclass(frozen=True)
class WorkerSettings:
    max_attempts: int
    retry_seconds: int
    claim_seconds: int

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "WorkerSettings":
        env = os.environ if environment is None else environment
        return cls(
            max_attempts=_positive_int(env.get("LUMEN_CLASSIFICATION_MAX_ATTEMPTS", "3"), "LUMEN_CLASSIFICATION_MAX_ATTEMPTS"),
            retry_seconds=_positive_int(env.get("LUMEN_CLASSIFICATION_RETRY_SECONDS", "10"), "LUMEN_CLASSIFICATION_RETRY_SECONDS"),
            claim_seconds=_positive_int(env.get("LUMEN_CLASSIFICATION_CLAIM_SECONDS", "120"), "LUMEN_CLASSIFICATION_CLAIM_SECONDS"),
        )


@dataclass(frozen=True)
class DecisionSettings:
    model: str
    api_key: str = field(repr=False)
    timeout_seconds: int

    @classmethod
    def from_environment(cls, claim_seconds: int, environment: Mapping[str, str] | None = None) -> "DecisionSettings":
        env = os.environ if environment is None else environment
        model = (env.get("LUMEN_DECISION_MODEL") or "").strip()
        api_key = (env.get("LUMEN_DECISION_API_KEY") or "").strip()
        if not model or not api_key:
            raise RuntimeError("Set LUMEN_DECISION_MODEL and LUMEN_DECISION_API_KEY in the worker environment.")
        timeout = _positive_int(env.get("LUMEN_DECISION_TIMEOUT_SECONDS", "60"), "LUMEN_DECISION_TIMEOUT_SECONDS")
        if timeout + 10 >= claim_seconds:
            raise RuntimeError("Decision timeout must be more than 10 seconds shorter than the classification claim lifetime.")
        return cls(model=model, api_key=api_key, timeout_seconds=timeout)


@dataclass(frozen=True)
class ResponseSettings:
    model: str
    api_key: str = field(repr=False)
    timeout_seconds: int

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "ResponseSettings":
        env = os.environ if environment is None else environment
        model = (env.get("LUMEN_RESPONSE_MODEL") or "").strip()
        api_key = (env.get("LUMEN_RESPONSE_API_KEY") or "").strip()
        if not model or not api_key:
            raise RuntimeError("Set LUMEN_RESPONSE_MODEL and LUMEN_RESPONSE_API_KEY in the worker environment.")
        timeout = _positive_int(env.get("LUMEN_RESPONSE_TIMEOUT_SECONDS", "60"), "LUMEN_RESPONSE_TIMEOUT_SECONDS", 120)
        return cls(model=model, api_key=api_key, timeout_seconds=timeout)


@dataclass(frozen=True)
class EmbeddingSettings:
    model: str
    dimensions: int
    api_key: str = field(repr=False)
    timeout_seconds: int

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "EmbeddingSettings":
        env = os.environ if environment is None else environment
        model = (env.get("LUMEN_EMBEDDING_MODEL") or "text-embedding-3-small").strip()
        api_key = (env.get("LUMEN_EMBEDDING_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("Set LUMEN_EMBEDDING_API_KEY in the worker environment.")
        dimensions = _positive_int(env.get("LUMEN_EMBEDDING_DIMENSIONS", "1536"), "LUMEN_EMBEDDING_DIMENSIONS", 16000)
        timeout = _positive_int(env.get("LUMEN_EMBEDDING_TIMEOUT_SECONDS", "30"), "LUMEN_EMBEDDING_TIMEOUT_SECONDS", 60)
        return cls(model, dimensions, api_key, timeout)


@dataclass(frozen=True)
class GenerationSettings:
    concurrency: int
    requests_per_window: int
    window_seconds: int
    max_attempts: int
    retry_seconds: int
    queue_limit: int
    input_price_per_million: Decimal | None = None
    output_price_per_million: Decimal | None = None
    currency: str | None = None
    claim_seconds: int = 360

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "GenerationSettings":
        env = os.environ if environment is None else environment
        def value(name: str, default: str) -> int:
            return _positive_int(env.get(name, default), name)
        raw_prices = (env.get("LUMEN_RESPONSE_INPUT_PRICE_PER_MILLION"), env.get("LUMEN_RESPONSE_OUTPUT_PRICE_PER_MILLION"), env.get("LUMEN_RESPONSE_CURRENCY"))
        if any(raw_prices) and not all(raw_prices):
            raise ValueError("Set both response prices and currency together.")
        prices = (None, None)
        currency = None
        if all(raw_prices):
            try:
                prices = (Decimal(raw_prices[0]), Decimal(raw_prices[1]))
                if any(not item.is_finite() or item < 0 for item in prices):
                    raise ValueError
            except (InvalidOperation, ValueError):
                raise ValueError("Response prices must be nonnegative decimal amounts.") from None
            currency = raw_prices[2].upper()
            if len(currency) != 3 or not currency.isascii() or not currency.isalpha():
                raise ValueError("Response currency must be a three-letter code.")
        return cls(value("LUMEN_RESPONSE_CONCURRENCY", "2"), value("LUMEN_RESPONSE_RATE_LIMIT", "20"), value("LUMEN_RESPONSE_RATE_WINDOW_SECONDS", "60"), value("LUMEN_RESPONSE_MAX_ATTEMPTS", "3"), value("LUMEN_RESPONSE_RETRY_SECONDS", "10"), value("LUMEN_RESPONSE_QUEUE_LIMIT", "100"), *prices, currency)
