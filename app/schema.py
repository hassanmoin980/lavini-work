from __future__ import annotations

VALUES = {"present", "denied", "unclear", "not_documented"}
RISK_FIELDS = (
    "current_suicidal_ideation",
    "historical_suicidal_ideation",
    "self_harm",
    "harm_to_others",
)
TOP_FIELDS = (
    "subjective",
    "objective",
    "assessment",
    "plan",
    "risk",
    "unsupported_or_uncertain_items",
    "model_used",
    "latency_ms",
    "estimated_cost_usd",
    "warnings",
)


def validate(note: dict, transcript: str) -> None:
    pass
