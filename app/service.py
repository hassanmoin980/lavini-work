from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .providers import NARRATIVE_FIELDS
from .router import choose_provider, rates_for
from .schema import validate

LOGGER = logging.getLogger("lavni.clinical_notes")

ATTEMPTS_PER_PROVIDER = 2

INJECTION_SIGNS = [
    "ignore all prior",
    "ignore previous",
    "disregard previous",
    "system:",
    "return exactly",
    "reveal the complete",
    "new instructions",
]


class AllProvidersFailed(Exception):
    pass


# def _provider_chain(transcript: str) -> list[Any]:
#     primary = choose_provider(transcript)
#     fallback = DeterministicProvider()
#     return [primary] if primary.name == fallback.name else [primary, fallback]


# def _try_provider(provider, transcript, intake, encounter_id, warnings):
#     for attempt in range(ATTEMPTS_PER_PROVIDER):
#         try:
#             with ThreadPoolExecutor(max_workers=1) as pool:
#                 note = pool.submit(provider.generate, transcript, intake).result(
#                     TIMEOUT_SECONDS
#                 )
#             note["model_used"] = provider.name
#             note["latency_ms"] = 0
#             note["estimated_cost_usd"] = 0
#             validate(note, transcript)
#             return note
#         except Exception as exc:
#             LOGGER.warning(
#                 "provider attempt failed encounter=%s provider=%s attempt=%s reason=%s",
#                 encounter_id,
#                 provider.name,
#                 attempt + 1,
#                 type(exc).__name__,
#             )
#     warnings.append(f"Provider {provider.name} failed; fell back.")
#     return None


def _try_provider(provider, transcript, intake, encounter_id, warnings):
    for attempt in range(ATTEMPTS_PER_PROVIDER):
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                note = pool.submit(provider.generate, transcript, intake).result(
                    provider.timeout_seconds
                )
            note["model_used"] = provider.name
            note["latency_ms"] = 0
            note["estimated_cost_usd"] = 0
            validate(note, transcript)
            return note
        except Exception as exc:
            LOGGER.warning(
                "provider attempt failed encounter=%s provider=%s attempt=%s reason=%s",
                encounter_id,
                provider.name,
                attempt + 1,
                type(exc).__name__,
            )
    warnings.append(f"Provider {provider.name} failed; fell back.")
    return None


def estimate_cost(
    transcript: str, output: dict[str, Any], model_name: str = ""
) -> float:
    rates = rates_for(model_name) if model_name else {"input": 0.80, "output": 0.80}

    usage = output.get("token_usage") or {}
    if usage.get("input") and usage.get("output"):
        in_tokens, out_tokens = usage["input"], usage["output"]
    else:
        generated = " ".join(str(output.get(f, "")) for f in NARRATIVE_FIELDS)
        in_tokens = len(transcript) / 4
        out_tokens = len(generated) / 4

    cost = (
        in_tokens * rates.get("input", 0.0) + out_tokens * rates.get("output", 0.0)
    ) / 1_000_000
    return round(cost, 6)

    # approximate_tokens = (len(transcript) + len(str(output))) / 4
    # price_per_million_tokens = 0.80
    # return round((approximate_tokens / 1_000_000) * price_per_million_tokens, 6)


def generate_note(payload: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    encounter_id = payload["encounter_id"]
    transcript = payload["transcript"]
    intake = payload.get("intake") or {}

    LOGGER.info("Generating note encounter=%s", encounter_id)

    warnings: list[str] = []
    if any(sign in transcript.lower() for sign in INJECTION_SIGNS):
        warnings.append("Transcript contains instruction-like text.")

    note = None
    for provider in choose_provider(transcript):
        note = _try_provider(provider, transcript, intake, encounter_id, warnings)
        if note is not None:
            break

    if note is None:
        LOGGER.error("no valid note produced encounter=%s", encounter_id)
        raise AllProvidersFailed("no provider returned a valid note")

    note["warnings"] = warnings + list(note.get("warnings") or [])
    if warnings:
        note["risk"]["requires_human_review"] = True

    note["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    note["estimated_cost_usd"] = estimate_cost(transcript, note, note["model_used"])
    LOGGER.info(
        "note generated encounter=%s model=%s review=%s",
        encounter_id,
        note["model_used"],
        note["risk"]["requires_human_review"],
    )
    return note

    # provider = choose_provider(transcript)
    # result = provider.generate(transcript, intake)
    # result["model_used"] = provider.name
    # result["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    # result["estimated_cost_usd"] = estimate_cost(transcript, result)
    # return result
