from collections import Counter

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


def clean(value):
    return value if value in VALUES else "ABSENT/INVALID"


def distribution(rows, index):
    if index == 1:
        print("Reference Labels:")
    elif index == 2:
        print("Risk:")

    for field in FIELDS:
        counts = Counter(
            clean(row[index].get(field) if isinstance(row[index], dict) else None)
            for row in rows
        )
        parts = [f"{v}={counts[v]}" for v in VALUES if counts[v]]
        if counts["ABSENT/INVALID"]:
            parts.append(f"ABSENT/INVALID={counts['ABSENT/INVALID']}")
        print(f"  {field:<30} {'  '.join(parts)}")


if __name__ == "__main__":
    records = load_jsonl(path=r".\data\public_cases.jsonl")
    records = add_risk_to_records(records)
    rows = collect(records)
    distribution(rows, 1)
    distribution(rows, 2)

    for field in FIELDS:
        TP = 0
        for _, expected, actual in rows:
            want = expected.get(field)
            got = clean(actual.get(field) if isinstance(actual, dict) else None)

            if want == got:
                TP += 1

    pass
