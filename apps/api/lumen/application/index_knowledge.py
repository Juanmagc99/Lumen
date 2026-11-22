"""Generate embeddings outside transactions and complete a leased index job."""

from lumen.application.embeddings import EmbeddingFailure


async def process_semantic_index(jobs, provider, settings, claim):
    key, chunks = claim
    vectors = []
    token_total = 0
    tokens_known = True
    try:
        if not chunks:
            raise EmbeddingFailure("empty")
        for offset in range(0, len(chunks), 32):
            if not await jobs.renew(key):
                return
            batch = chunks[offset:offset + 32]
            result = await provider.embed([row.content for row in batch])
            vectors.extend((row.id, vector) for row, vector in zip(batch, result.vectors, strict=True))
            if result.input_tokens is None:
                tokens_known = False
            else:
                token_total += result.input_tokens
        current = settings()
        if (current.model, current.dimensions) != (key["model"], key["dimensions"]):
            raise EmbeddingFailure("configuration_changed")
        await jobs.finish(key, vectors, token_total if tokens_known else None)
    except (EmbeddingFailure, RuntimeError, ValueError):
        await jobs.finish(key, [], None, failure=True)
