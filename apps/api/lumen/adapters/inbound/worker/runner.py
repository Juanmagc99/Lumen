"""Poll for durable jobs and invoke classification."""

import asyncio
import logging

from lumen.application.classification_ports import ClassificationJobs
from lumen.application.classify_ticket import ClassifyTicket
from lumen.application.ingest_knowledge import process_ingestion
from lumen.application.index_knowledge import process_semantic_index

logger = logging.getLogger("lumen.worker")


async def run_semantic_index(jobs, provider, settings) -> None:
    while True:
        try:
            claim = await jobs.claim(settings())
            if claim is None:
                await asyncio.sleep(2)
            else:
                await process_semantic_index(jobs, provider, settings, claim)
        except Exception:
            logger.warning("Semantic indexing unavailable; retrying")
            await asyncio.sleep(10)


async def run_ingestion(jobs) -> None:
    while True:
        try:
            claim = await jobs.claim()
            if claim is None:
                await asyncio.sleep(2)
            else:
                await process_ingestion(jobs, claim)
        except Exception:
            logger.warning("Ingestion storage operation failed; retrying")
            await asyncio.sleep(2)


async def run_generation(jobs, generate) -> None:
    while True:
        try:
            claim = await jobs.claim()
            if claim is None:
                await asyncio.sleep(2)
            else:
                await generate.process(claim)
        except Exception:
            logger.warning("Generation storage operation failed; retrying")
            await asyncio.sleep(2)


async def run(jobs: ClassificationJobs, classify: ClassifyTicket) -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Classification worker started")
    while True:
        try:
            claim = await jobs.claim()
            if claim is None:
                await asyncio.sleep(2)
                continue
            failure = await classify.process(claim)
            if failure:
                logger.warning("Classification attempt failed: %s", failure)
        except Exception:
            logger.warning("Worker storage operation failed; retrying")
            await asyncio.sleep(2)
