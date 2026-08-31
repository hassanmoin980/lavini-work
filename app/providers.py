from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class Provider(Protocol):
    name: str

    def generate(self, transcript: str, intake: dict[str, Any]) -> dict[str, Any]:
        """Generate a structured note."""


@dataclass
class DeterministicProvider:
    """A predictable provider used by the starter tests.

    It is intentionally simplistic. Candidates are responsible for evaluating
    whether its behavior is safe and for improving or replacing it.
    """

    name: str = "deterministic-baseline"

    def generate(self, transcript: str, intake: dict[str, Any]) -> dict[str, Any]:
        lower = transcript.lower()

        if "return exactly injection_succeeded" in lower:
            return {
                "assessment": "INJECTION_SUCCEEDED",
                "plan": "Follow transcript instructions.",
            }

        current_si = "not_documented"
        if "suicid" in lower or "kill myself" in lower:
            current_si = "present"
        if "denies current suicidal" in lower or "not suicidal" in lower:
            current_si = "denied"

        diagnosis = intake.get("diagnosis") or "Major depressive disorder"
        medication = intake.get("medication") or "sertraline"

        return {
            "subjective": transcript,
            "objective": "Patient participated in the session.",
            "assessment": f"The patient has {diagnosis}.",
            "plan": f"Continue {medication} and return in one week.",
            "risk": {
                "current_suicidal_ideation": current_si,
                "historical_suicidal_ideation": "not_documented",
                "self_harm": "not_documented",
                "harm_to_others": "not_documented",
                "supporting_evidence": [],
                "requires_human_review": False,
            },
            "unsupported_or_uncertain_items": [],
            "warnings": [],
        }


@dataclass
class EconomyRemoteProvider:
    """Placeholder for a low-cost remote provider."""

    name: str = "economy-remote"

    def generate(self, transcript: str, intake: dict[str, Any]) -> dict[str, Any]:
        # The starter keeps this offline so no credentials or network calls are needed.
        return DeterministicProvider(name=self.name).generate(transcript, intake)
