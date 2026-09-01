from .service import generate_note


def add_risk_to_records(records):
    for i, record in enumerate(records):
        note = generate_note(record)
        records[i]["risk"] = note.get("risk") if isinstance(note, dict) else None
    return records
