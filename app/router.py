from __future__ import annotations

from .providers import DeterministicProvider, EconomyRemoteProvider, Provider


def choose_provider(transcript: str) -> Provider:
    """Choose a provider using the prototype's initial cost-oriented rule."""
    lower = transcript.lower()
    if len(transcript) > 900 or "suicid" in lower or "self-harm" in lower:
        return EconomyRemoteProvider()
    return DeterministicProvider()
