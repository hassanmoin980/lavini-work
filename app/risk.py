from __future__ import annotations

import re

TERMS = {
    "suicidal_ideation": [
        "suicid",
        "kill myself",
        "killing myself",
        "end my life",
        "want to die",
        "wanting to die",
        "take my own life",
    ],
    "self_harm": [
        "self-harm",
        "self harm",
        "cut myself",
        "cutting myself",
        "scratch",
        "burn myself",
        "hurt myself",
        "hurting myself",
    ],
    "harm_to_others": [
        "hurt someone",
        "hurting someone",
        "harm others",
        "harm someone",
        "violent toward",
        "attack them",
    ],
}

NEGATION = ["deny", "denies", "denied", " no ", " not ", "n't", "without", "never"]
PAST = ["since", "last ", " ago", "used to", "previously", "in the past", "history of"]
NOW = ["today", "currently", "right now", "tonight", "this morning", "at present"]

PRECEDENCE = ["present", "unclear", "denied", "not_documented"]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _clauses(sentence: str) -> list[str]:
    return [
        c for c in re.split(r"[,;]| but | although | however ", sentence) if c.strip()
    ]


def _has(clause: str, words: list[str]) -> bool:
    padded = f" {clause.lower()} "
    return any(word in padded for word in words)


if __name__ == "__main__":
    print(_sentences("my name is hassan. i am an Sr AI dev"))
    print(
        _clauses("my name is hassan, but i am an Sr AI dev, although i did engineering")
    )
    print(_has("my name is hassan, I work as a developer", ["dev"]))
