import json

from .dataset import load_jsonl
from .service import generate_note

FIELDS = [
    "current_suicidal_ideation",
    "historical_suicidal_ideation",
    "self_harm",
    "harm_to_others",
]

VALUES = ["present", "denied", "unclear", "not_documented"]


def add_risk_to_records(records):
    for i, record in enumerate(records):
        note = generate_note(record)
        records[i]["risk"] = note.get("risk") if isinstance(note, dict) else None
    return records


def collect(records):
    rows = []
    for record in records:
        rows.append(
            (
                record.get("case_id"),
                record.get("reference_labels"),
                record.get("risk", {}),
            )
        )
    return rows


if __name__ == "__main__":
    records = load_jsonl(path=r".\data\public_cases.jsonl")
    records = add_risk_to_records(records)
    rows = collect(records)
    pass
