from __future__ import annotations

from . import providers
from .config import load_models
from .risk import assess

ORDER_WITH_RISK = ["strong", "economy", "fallback"]
ORDER_NO_RISK = ["economy", "strong", "fallback"]


def choose_provider(transcript: str) -> list:
    """Choose a provider using the prototype's initial cost-oriented rule."""
    values, _ = assess(transcript)
    risky = any(v in {"present", "unclear"} for v in values.values())
    order = ORDER_WITH_RISK if risky else ORDER_NO_RISK

    enabled = load_models()
    chain = [m for tier in order for m in enabled if m.get("tier") == tier]
    return [providers.build(m) for m in chain]

    # lower = transcript.lower()
    # if len(transcript) > 900 or "suicid" in lower or "self-harm" in lower:
    #     return EconomyRemoteProvider()
    # return DeterministicProvider()


def rates_for(name: str) -> dict:
    for model in load_models():
        if model["name"] == name:
            return model.get("usd_per_million", {})
    return {"input": 0.0, "output": 0.0}
