from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .router import choose_provider

LOGGER = logging.getLogger("lavni.clinical_notes")

TIMEOUT_SECONDS = 8.0
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


def estimate_cost(transcript: str, output: dict[str, Any]) -> float:
    approximate_tokens = (len(transcript) + len(str(output))) / 4
    price_per_million_tokens = 0.80
    return round((approximate_tokens / 1_000_000) * price_per_million_tokens, 6)


def generate_note(payload: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    encounter_id = payload["encounter_id"]
    transcript = payload["transcript"]
    intake = payload.get("intake") or {}

    LOGGER.info("Generating note encounter=%s transcript=%s", encounter_id, transcript)
    provider = choose_provider(transcript)
    result = provider.generate(transcript, intake)
    result["model_used"] = provider.name
    result["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    result["estimated_cost_usd"] = estimate_cost(transcript, result)
    return result
