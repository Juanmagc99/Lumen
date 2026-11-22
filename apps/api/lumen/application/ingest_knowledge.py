"""Split persisted knowledge text into bounded retrieval fragments."""


def split_content(content: str, size: int = 1200) -> list[str]:
    chunks = []
    remaining = content.strip()
    while remaining:
        if len(remaining) <= size:
            chunks.append(remaining)
            break
        end = remaining.rfind(" ", 0, size + 1)
        if end < size // 2:
            end = size
        chunks.append(remaining[:end])
        remaining = remaining[end:].lstrip()
    return chunks


async def process_ingestion(jobs, claim):
    try:
        chunks = split_content(claim[2])
        if not chunks:
            raise ValueError("No usable content")
    except Exception:
        await jobs.finish(claim, None)
        return
    await jobs.finish(claim, chunks)
