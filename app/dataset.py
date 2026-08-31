from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


def load_jsonl(path: str) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def random_split(records: list[dict[str, Any]], test_fraction: float = 0.25) -> tuple[list, list]:
    shuffled = list(records)
    random.Random(7).shuffle(shuffled)
    boundary = max(1, int(len(shuffled) * (1 - test_fraction)))
    return shuffled[:boundary], shuffled[boundary:]
