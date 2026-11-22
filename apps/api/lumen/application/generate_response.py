"""Coordinate retrieval, call admission, generation and audit completion."""

from lumen.application.response_model import GeneratedResponse, ResponseModelFailure
from lumen.application.retrieval import RetrievalResult


class GenerateResponse:
    def __init__(self, jobs, retriever, model, settings):
        self.jobs, self.retriever, self.model, self.settings = jobs, retriever, model, settings

    async def process(self, claim):
        base_id = claim["knowledge_base_id"]
        retrieval = await self.retriever.retrieve(base_id, f'{claim["subject"]} {claim["description"]}') if base_id is not None else RetrievalResult([], "none")
        evidence = retrieval.evidence
        if base_id is not None and not evidence:
            attempt = await self.jobs.begin_attempt(claim, [], None, False, retrieval)
            if attempt:
                result = GeneratedResponse("There is not enough information in the selected knowledge base to draft a grounded response.", "No matching source was retrieved.", (), True, None, None, None, None)
                await self.jobs.finish(claim, attempt, result=result)
            return
        try:
            self.model.validate_configuration()
            model_name = self.settings().model
        except (ResponseModelFailure, RuntimeError, ValueError):
            attempt = await self.jobs.begin_attempt(claim, evidence, None, False, retrieval)
            if attempt:
                await self.jobs.finish(claim, attempt, failure="configuration")
            return
        attempt = await self.jobs.begin_attempt(claim, evidence, model_name, True, retrieval)
        if attempt is None:
            return
        try:
            result = await self.model.generate(claim["subject"], claim["description"], evidence)
        except ResponseModelFailure as exc:
            await self.jobs.finish(claim, attempt, failure=str(exc))
            return
        await self.jobs.finish(claim, attempt, result=result)
