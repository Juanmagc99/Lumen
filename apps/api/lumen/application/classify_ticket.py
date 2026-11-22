"""Coordinate one durable classification attempt."""

from lumen.application.classification_ports import ClassificationJobs, DecisionModel
from lumen.domain.classification import ClaimedClassification, ClassificationFailure


class ClassifyTicket:
    def __init__(self, jobs: ClassificationJobs, model: DecisionModel):
        self._jobs = jobs
        self._model = model

    async def process(self, claim: ClaimedClassification) -> str | None:
        try:
            self._model.validate_configuration()
            options = await self._jobs.active_options()
            categories = [option for option in options if option.kind == "category"]
            priorities = [option for option in options if option.kind == "priority"]
            if not categories or not priorities:
                raise ClassificationFailure("no_options")
            decision = await self._model.decide(claim.subject, claim.description, categories, priorities)
            if len(decision.category_ids) != len(set(decision.category_ids)) or not set(decision.category_ids).issubset({option.id for option in categories}) or (decision.priority_id is not None and decision.priority_id not in {option.id for option in priorities}):
                raise ClassificationFailure("invalid_decision")
        except ClassificationFailure as exc:
            await self._jobs.finish(claim, failure_reason=str(exc))
            return str(exc)
        await self._jobs.finish(claim, decision=decision)
        return None
