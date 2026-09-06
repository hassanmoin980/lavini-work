"""Section 5: report dataset defects. Reports only - never repairs.

python3 -m app.dataset_audit --data data/public_cases.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from itertools import combinations

from .dataset import load_jsonl

RISK = (
    "current_suicidal_ideation",
    "historical_suicidal_ideation",
    "self_harm",
    "harm_to_others",
)
IDENTIFIER = re.compile(r"\d{3}-\d{2}-\d{4}|\d{3}-\d{3}-\d{4}|CANARY[A-Z0-9-]*", re.I)
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T")
NEAR_DUPLICATE = 0.35


def _shingles(text: str) -> set[str]:
    text = re.sub(r"\s+", " ", text.lower()).strip()
    return {text[i : i + 5] for i in range(len(text) - 4)}


def _similarity(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def audit(records: list[dict]) -> dict:
    report = {
        "records": len(records),
        "splits": dict(Counter(r["split"] for r in records)),
    }
    report["duplicates"] = [
        {
            "cases": [a["case_id"], b["case_id"]],
            "similarity": round(
                _similarity(_shingles(a["transcript"]), _shingles(b["transcript"])), 3
            ),
            "same_patient_key": a["patient_key"] == b["patient_key"],
            "splits": sorted({a["split"], b["split"]}),
        }
        for a, b in combinations(records, 2)
        if _similarity(_shingles(a["transcript"]), _shingles(b["transcript"]))
        >= NEAR_DUPLICATE
    ]
    report["duplicates_across_splits"] = [
        d for d in report["duplicates"] if len(d["splits"]) > 1
    ]

    seen: dict[str, set] = {}
    for r in records:
        seen.setdefault(r["patient_key"], set()).add(r["split"])
    report["patients_in_two_splits"] = [
        {"patient_key": k, "splits": sorted(v)} for k, v in seen.items() if len(v) > 1
    ]

    report["bad_chronology"] = [
        {
            "case": r["case_id"],
            "note": "intake recorded after the encounter it describes",
        }
        for r in records
        if r.get("intake_recorded_at", "") > r.get("occurred_at", "")
        and TIMESTAMP.match(r.get("occurred_at", ""))
    ]

    report["malformed"] = [
        {
            "case": r.get("case_id", "?"),
            "problems": ([] if r.get("patient_key") else ["empty patient_key"])
            + (
                []
                if TIMESTAMP.match(str(r.get("occurred_at", "")))
                else ["bad occurred_at"]
            ),
        }
        for r in records
        if not r.get("patient_key")
        or not TIMESTAMP.match(str(r.get("occurred_at", "")))
    ]

    report["sensitive_values"] = [
        {"case": r["case_id"], "matches": len(IDENTIFIER.findall(r["transcript"]))}
        for r in records
        if IDENTIFIER.search(r["transcript"])
    ]

    report["contradictory_labels"] = [
        {
            "case": r["case_id"],
            "note": "intake says medication active, transcript says stopped",
        }
        for r in records
        if (r.get("intake") or {}).get("medication_status") == "active"
        and "stopped taking" in r["transcript"].lower()
    ]

    report["label_leakage"] = {
        "records_carrying_labels": sum("reference_labels" in r for r in records),
        "note": "strip reference_labels before a record reaches a provider",
    }

    combos = Counter(tuple(r["reference_labels"][f] for f in RISK) for r in records)
    common, n = combos.most_common(1)[0]
    report["class_imbalance"] = {
        "per_field": {
            f: dict(Counter(r["reference_labels"][f] for r in records)) for f in RISK
        },
        "most_common_combination": list(common),
        "majority_baseline_accuracy": round(n / len(records), 3),
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None)
    parser.add_argument("--out", default="dataset-audit.json")
    args = parser.parse_args()

    report = audit(load_jsonl(args.data))
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    for key, value in report.items():
        if isinstance(value, list):
            print(f"{key:28} {len(value)}")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
