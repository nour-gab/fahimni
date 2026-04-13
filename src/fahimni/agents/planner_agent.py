"""Planner agent for personalized adaptive study plans."""

from collections.abc import Sequence

from fahimni.services.ai_service import AIService


class PlannerAgent:
    """Agent that creates structured learning paths."""

    def __init__(self, ai_service: AIService | None = None) -> None:
        self._ai = ai_service or AIService()

    def build_plan(
        self,
        weak_topics: Sequence[str],
        study_minutes_per_day: int,
        horizon_days: int,
    ) -> dict[str, object]:
        return self._ai.generate_learning_path(
            weak_topics=list(weak_topics),
            study_minutes_per_day=study_minutes_per_day,
            horizon_days=horizon_days,
        )
