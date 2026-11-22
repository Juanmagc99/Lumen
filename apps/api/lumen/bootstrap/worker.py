"""Compose the classification worker and its adapters."""

import asyncio
import os

# Local settings are loaded by the development launcher, not by dependencies.
os.environ["PYTHON_DOTENV_DISABLED"] = "1"

from lumen.adapters.inbound.worker.runner import run, run_ingestion, run_generation, run_semantic_index
from lumen.adapters.outbound.db.classification_jobs import PostgresClassificationJobs
from lumen.adapters.outbound.db.ingestion_jobs import PostgresIngestionJobs
from lumen.adapters.outbound.db.semantic_index import PostgresSemanticIndex
from lumen.adapters.outbound.db.response_generations import PostgresResponseGenerations
from lumen.adapters.outbound.db.retrieval import PostgresRetriever
from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.adapters.outbound.llm.litellm_model import LiteLLMDecisionModel
from lumen.adapters.outbound.llm.response_model import LiteLLMResponseModel
from lumen.adapters.outbound.llm.embeddings import OpenAIEmbeddingProvider
from lumen.application.classify_ticket import ClassifyTicket
from lumen.bootstrap.config import DecisionSettings, WorkerSettings, GenerationSettings, ResponseSettings, EmbeddingSettings, database_url
from lumen.application.generate_response import GenerateResponse
from lumen.domain.classification import ClassificationPolicy


def main() -> None:
    settings = WorkerSettings.from_environment()
    policy = ClassificationPolicy(settings.max_attempts, settings.retry_seconds, settings.claim_seconds)
    jobs = PostgresClassificationJobs(policy, DatabaseSessions(database_url))
    model = LiteLLMDecisionModel(lambda: DecisionSettings.from_environment(settings.claim_seconds))
    generation_jobs = PostgresResponseGenerations(DatabaseSessions(database_url), GenerationSettings.from_environment())
    response_settings = lambda: ResponseSettings.from_environment()
    embedding_settings = lambda: EmbeddingSettings.from_environment()
    generate = GenerateResponse(generation_jobs, PostgresRetriever(DatabaseSessions(database_url), OpenAIEmbeddingProvider(embedding_settings), embedding_settings), LiteLLMResponseModel(response_settings), response_settings)
    async def run_workers():
        await asyncio.gather(run(jobs, ClassifyTicket(jobs, model)), run_ingestion(PostgresIngestionJobs(DatabaseSessions(database_url))), run_generation(generation_jobs, generate), run_semantic_index(PostgresSemanticIndex(DatabaseSessions(database_url)), OpenAIEmbeddingProvider(embedding_settings), embedding_settings))
    asyncio.run(run_workers())


if __name__ == "__main__":
    main()
