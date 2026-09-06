from __future__ import annotations

# PyDantic?

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


class InvalidNote(Exception):
    pass


def validate(note: dict, transcript: str) -> None:
    if not isinstance(note, dict):
        raise InvalidNote("note is not an object")

    for field in TOP_FIELDS:
        if field not in note:
            raise InvalidNote(f"missing field: {field}")

    if not isinstance(note["risk"], dict):
        raise InvalidNote("risk is not an object")

    for field in RISK_FIELDS:
        if note["risk"].get(field) not in VALUES:
            raise InvalidNote(f"bad value for {field}: {note['risk'].get(field)!r}")

    asserted = any(note["risk"].get(f) in {"present", "unclear"} for f in RISK_FIELDS)
    evidence = note["risk"].get("supporting_evidence") or []

    if asserted and not evidence:
        raise InvalidNote("risk asserted without supporting evidence")

    for span in evidence:
        if span.get("quote", "") not in transcript:
            raise InvalidNote("supporting evidence is not in the transcript")

    if asserted and note["risk"].get("requires_human_review") is not True:
        raise InvalidNote("risk asserted but human review not required.")
