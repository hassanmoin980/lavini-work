from __future__ import annotations

import re
import typing

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


def _worst(values: list[str]) -> str:
    for level in PRECEDENCE:
        if level in values:
            return level
    return "not_documented"


def assess(transcript: str) -> typing.Tuple[dict, list[dict]]:
    current, historical, harm, others = [], [], [], []
    evidence: list[dict] = []
    for sentence in _sentences(transcript):
        for clause in _clauses(sentence):
            for dim, terms in TERMS.items():
                if not _has(clause, terms):
                    continue

                negated = _has(clause, NEGATION)
                past = _has(clause, PAST)
                now = _has(clause, NOW)
                evidence.append({"dimension": dim, "quote": sentence})

                if dim == "self_harm":
                    harm.append("denied" if negated else "present")
                elif dim == "harm_to_others":
                    others.append("denied" if negated else "present")
                elif negated and past:
                    current.append("denied")
                    historical.append("present")
                elif negated:
                    current.append("denied")
                elif past:
                    historical.append("present")
                elif now:
                    current.append("present")
                else:
                    current.append("unclear")

    return {
        "current_suicidal_ideation": _worst(current),
        "historical_suicidal_ideation": _worst(historical),
        "self_harm": _worst(harm),
        "harm_to_others": _worst(others),
    }, evidence


if __name__ == "__main__":
    print(_sentences("my name is hassan. i am an Sr AI dev"))
    print(
        _clauses("my name is hassan, but i am an Sr AI dev, although i did engineering")
    )
    print(_has("my name is hassan, I work as a developer", ["dev"]))
    print(assess("I am going to kill myself today"))
    print(assess("I am not going to kill myself today"))
