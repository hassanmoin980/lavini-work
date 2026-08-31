from __future__ import annotations

import argparse
import json

from .analysis_h import add_risk_to_records
from .dataset import load_jsonl, random_split
from .service import generate_note


def score_note(transcript: str, note: dict) -> float:
    """Starter quality heuristic based on simple word overlap."""
    transcript_words = set(transcript.lower().split())
    note_words = set(str(note).lower().split())
    return round(len(transcript_words & note_words) / max(1, len(transcript_words)), 3)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()
    records = load_jsonl(args.data)

    # --------DATA ANALYSIS----------- #
    records = add_risk_to_records(records)

    pass

    # -------------------------------- #

    _, evaluation_records = random_split(records)
    rows = []
    for record in evaluation_records:
        note = generate_note(record)
        rows.append(
            {
                "case_id": record.get("case_id"),
                "quality_score": score_note(record["transcript"], note),
            }
        )
    result = {
        "evaluated": len(rows),
        "average_quality": round(
            sum(r["quality_score"] for r in rows) / max(1, len(rows)), 3
        ),
        "cases": rows,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
