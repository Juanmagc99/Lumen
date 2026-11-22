"""Bounded OpenAI embedding calls through the existing LiteLLM dependency."""

import asyncio
import math
from collections.abc import Callable

import litellm

from lumen.application.embeddings import EmbeddingBatch, EmbeddingFailure


class OpenAIEmbeddingProvider:
    def __init__(self, settings: Callable):
        self._settings = settings

    async def embed(self, texts: list[str]) -> EmbeddingBatch:
        if not texts or len(texts) > 32 or any(not text.strip() or len(text) > 20000 for text in texts):
            raise EmbeddingFailure("invalid_input")
        try:
            settings = self._settings()
        except (ValueError, RuntimeError):
            raise EmbeddingFailure("configuration") from None
        for attempt in range(2):
            try:
                response = await asyncio.wait_for(
                    litellm.aembedding(model=f"openai/{settings.model}", input=texts, dimensions=settings.dimensions,
                                      api_key=settings.api_key, timeout=settings.timeout_seconds, num_retries=0),
                    timeout=settings.timeout_seconds,
                )
                items = sorted(response.data, key=lambda item: item["index"])
                if [item["index"] for item in items] != list(range(len(texts))):
                    raise ValueError("Invalid embedding indices")
                vectors = tuple(tuple(float(value) for value in item["embedding"]) for item in items)
                if any(len(vector) != settings.dimensions or any(not math.isfinite(v) for v in vector) or not any(vector) for vector in vectors):
                    raise ValueError("Invalid embedding vectors")
                usage = getattr(response, "usage", None)
                tokens = getattr(usage, "prompt_tokens", None)
                if not isinstance(tokens, int) or tokens < 0:
                    tokens = None
                return EmbeddingBatch(vectors, tokens)
            except Exception:
                if attempt == 0:
                    await asyncio.sleep(1)
        raise EmbeddingFailure("provider") from None
