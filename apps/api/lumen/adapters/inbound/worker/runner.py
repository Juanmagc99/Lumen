"""Poll for durable jobs and invoke classification."""

import asyncio
import logging

from lumen.application.classification_ports import ClassificationJobs
from lumen.application.classify_ticket import ClassifyTicket
from lumen.application.ingest_knowledge import process_ingestion
from lumen.application.index_knowledge import process_semantic_index

logger = logging.getLogger("lumen.worker")


def log_failure(operation: str, exc: Exception) -> None:
    logger.error("worker_operation_failed", extra={"operation": operation})


async def run_semantic_index(jobs, provider, settings) -> None:
    while True:
        try:
            claim = await jobs.claim(settings())
            if claim is None:
                await asyncio.sleep(2)
            else:
                await process_semantic_index(jobs, provider, settings, claim)
        except Exception as exc:
            log_failure("semantic_index", exc)
            await asyncio.sleep(10)


async def run_ingestion(jobs) -> None:
    while True:
        try:
            claim = await jobs.claim()
            if claim is None:
                await asyncio.sleep(2)
            else:
                await process_ingestion(jobs, claim)
        except Exception as exc:
            log_failure("ingestion", exc)
            await asyncio.sleep(2)


async def run_generation(jobs, generate) -> None:
    while True:
        try:
            claim = await jobs.claim()
            if claim is None:
                await asyncio.sleep(2)
            else:
                await generate.process(claim)
        except Exception as exc:
            log_failure("generation", exc)
            await asyncio.sleep(2)


async def run(jobs: ClassificationJobs, classify: ClassifyTicket) -> None:
    logger.info("worker_started", extra={"operation": "classification"})
    while True:
        try:
            claim = await jobs.claim()
            if claim is None:
                await asyncio.sleep(2)
                continue
            failure = await classify.process(claim)
            if failure:
                logger.warning("classification_attempt_failed", extra={"operation": "classification"})
        except Exception as exc:
            log_failure("classification", exc)
            await asyncio.sleep(2)
