# Lavni clinical-note service

Generates a structured clinical-note draft from a therapy-session transcript. This started
as the supplied prototype and has been repaired - the original had problems with clinical
accuracy, hallucination, data leakage, evaluation, logging, routing, error handling, cost
estimation and prompt injection.

**Every note is a draft requiring clinician review. Nothing here produces a signed clinical
document.**

Synthetic data only. No real PHI, credentials or proprietary material in this repo.

## The one design decision that matters

**A model never decides risk.** `app/risk.py` extracts risk from the transcript in code and
quotes the sentence it came from. The model only writes the narrative fields - subjective,
objective, assessment, plan.

Every provider builds its note through `_assemble()` in `app/providers.py`, which always
calls `risk.assess()`. So a worse model gives worse prose; it cannot move a risk field.
There's a test for it: a fake model that returns `not_documented` on a transcript about
active ideation still yields `present`.

## Quick start

No third-party packages. Python 3.10+.

```bash
make run        # serve on http://127.0.0.1:8080
make test       # 67 tests
make evaluate   # release gate, writes evaluation-results.json
python3 -m app.dataset_audit    # dataset audit, writes dataset-audit.json
```

Docker:

```bash
docker build -t lavni-notes .
docker run -p 8080:8080 lavni-notes
```

Only the deterministic provider is enabled out of the box, so everything above runs with no
credentials and no network.

## Using the API

Same interface as the original: `POST /v1/clinical-notes`, `GET /health`.

```bash
curl -s http://localhost:8080/v1/clinical-notes \
  -H "Content-Type: application/json" \
  -d '{"encounter_id":"demo-1","transcript":"I am having thoughts of killing myself today.","intake":{}}'
```

Windows cmd - use `python`, and escape the inner quotes:

```
curl -s http://localhost:8080/v1/clinical-notes -H "Content-Type: application/json" -d "{\"encounter_id\":\"demo-1\",\"transcript\":\"I am having thoughts of killing myself today.\"}"
```

`intake` is optional. Response carries the ten contract fields, and every risk claim comes
with the transcript sentence that supports it:

```json
{
  "risk": {
    "current_suicidal_ideation": "present",
    "historical_suicidal_ideation": "not_documented",
    "self_harm": "not_documented",
    "harm_to_others": "not_documented",
    "supporting_evidence": [
      {"dimension": "suicidal_ideation", "quote": "I am having thoughts of killing myself today."}
    ],
    "requires_human_review": true
  },
  "unsupported_or_uncertain_items": ["..."],
  "warnings": ["..."],
  "model_used": "deterministic-baseline",
  "latency_ms": 1.39,
  "estimated_cost_usd": 0.0
}
```

Status codes: `200` on success, `400` for a malformed request, `503` when no provider could
produce a valid note, `500` otherwise. Error bodies carry a generic message plus a reference
id - never the transcript.

## How a request flows

1. `server.py` - HTTP, bounded body read, status mapping.
2. `service.py` - checks `encounter_id` and `transcript`, scans for instruction-like text, walks the provider chain, validates, attaches `model_used` / `latency_ms` / `estimated_cost_usd`, logs metadata only.
3. `router.py` - `choose_providers()` returns an ordered chain. Risk `present` or `unclear` puts the strong tier first; otherwise the economy tier leads. `DeterministicProvider` is always last.
4. `providers.py` - the selected provider writes narrative; `_assemble()` adds risk from `risk.py`.
5. `schema.py` - `validate()` before anything is returned. A failure counts as a provider failure, not a bad note to pass on.

Each provider gets its configured timeout and one retry. Timeout, crash and invalid output
all take the same path: log the failure type, add a warning, try the next provider. If none
succeed, no note is returned at all - `503`, never a partial.

## Routing and fallback

Configured in `app/models.json`. Nothing about model choice lives in code.

```json
{
  "name": "llama-3.1-8b-instruct",
  "kind": "openai_compatible",
  "tier": "economy",
  "enabled": false,
  "base_url": "https://router.huggingface.co/v1",
  "model": "meta-llama/Llama-3.1-8B-Instruct",
  "api_key_env": "HF_TOKEN",
  "timeout_seconds": 20,
  "usd_per_million": { "input": 0.01, "output": 0.05 }
}
```

- `tier` is `economy`, `strong` or `fallback`. Order with risk: strong, economy, fallback. Without: economy, strong, fallback.
- `enabled: false` removes a model from every chain. **That is the rollback mechanism** - config change, no code change, no service redeploy.
- `timeout_seconds` and `usd_per_million` are per model.
- `MODELS_CONFIG` points at a different file if you need one.

`OpenAICompatibleProvider` speaks the OpenAI `/chat/completions` shape, so Hugging Face,
Ollama, vLLM, Together and Groq all work by changing `base_url`. Standard library only, so
the Docker image needs no dependency step.

To enable a real model: `cp .env.example .env`, add `HF_TOKEN`, set `"enabled": true`.

## Evaluation

```bash
make evaluate
```

Prints a summary and writes `evaluation-results.json`. Two groups, deliberately separate:

- **Graded** - the `test` split only (PUB-007, PUB-008, PUB-011, PUB-012). Generalisation numbers.
- **Safety probes** - every other case, safety checks only. Injection resistance and PHI leakage are properties of the system, not claims about unseen data, so they aren't held out. A probe failure blocks release just like a graded one.

Three outcomes: `unsafe`, `requires_improvement`,
`acceptable_for_clinician_reviewed_drafting`. Safety failures aren't tradeable against good
averages - one missed current risk is `unsafe` however well everything else scores.

Current output:

```
"release_outcome": "requires_improvement",
"risk_fields_correct": "16/16",
"schema_valid": 12,
"faithfulness_failures": 12,
"leakage_failures": 1
```

**Read that as the metrics working, not the service failing.** Risk classification is
correct on all four fields across all cases - down from 9 mismatches in the original. The
faithfulness failures are the inherited default diagnosis and medication, which the
deterministic provider still emits and now declares in
`unsupported_or_uncertain_items`. The single leakage failure is PUB-006, where the note
copies the transcript verbatim into `subjective` and carries the supplied canary with it.

`--llm-judge <model>` adds an advisory signal. It writes to `llm_judge_advisory` and never
feeds the gate - see `EVALUATION.md` for why.

## Dataset audit

```bash
python3 -m app.dataset_audit --data data/public_cases.jsonl
```

Prints counts and writes `dataset-audit.json`. Reports only - never repairs. A corpus is
evidence, and quietly fixing it destroys the record of what was wrong.

```
duplicates                   3
duplicates_across_splits     2
patients_in_two_splits       1
bad_chronology               1
malformed                    1
sensitive_values             1
contradictory_labels         1
```

The one worth reading: PUB-008 is a paraphrase of PUB-002 and PUB-007 filed under
`patient_key: "SYN-P002-ALT"`. Grouping by patient key alone misses it, so the audit also
clusters by text similarity - Jaccard over 5-character shingles, threshold 0.35, picked from
the observed distribution (real paraphrases score ~0.45, unrelated pairs peak at ~0.22).
`sensitive_values` reports counts and case ids only; writing the values would be the leak
it's looking for.

## Open-weight experiment

```bash
export HF_TOKEN=hf_...          # or put it in .env
# set "enabled": true for the model in app/models.json
python3 -m experiments.run_open_weight --model llama-3.1-8b-instruct
```

Runs all twelve cases and reports schema validity, risk correctness, injection leaks,
p50/p95 latency and cost. Results template in `experiments/RESULTS.md`.

## Layout

```
app/
  server.py          HTTP layer
  service.py         orchestration, timeout, retry, fallback, cost, logging
  router.py          config-driven provider chain, risk escalation
  providers.py       DeterministicProvider, OpenAICompatibleProvider
  risk.py            risk extraction with quoted evidence
  schema.py          output contract validation
  config.py          models.json + .env loader
  models.json        model registry - tiers, rates, timeouts, enable flags
  evaluation.py      release gate
  dataset_audit.py   dataset validation
  dataset.py         jsonl loader (unchanged from the starter)
tests/               67 tests
experiments/         open-weight harness and results
data/                supplied synthetic cases - treat as untrusted input
```

## Documents

| File | What's in it |
|---|---|
| `FINDINGS.md` | Problems found in the prototype, with severity, evidence and status |
| `DECISIONS.md` | Model strategy - prompting vs fine-tuning, routing, promotion, rollback, training-data rules, memorisation testing |
| `EVALUATION.md` | What the metrics measure and what they miss |
| `DATASET.md` | Audit findings and how to split without patient overlap |
| `COST.md` | Cost at 10k/50k/250k, three delivery options, break-even, and the answer to the $2,000 question |
| `THREAT.md` | Threat model and what's required before real PHI |

## Known gaps

Stated here rather than left to be found.

- **`model_used` has no version.** It reports a family name. Rollback works; identifying which notes came from a bad model version does not.
- **No emergency escalation.** A note is not an alert. If active suicidal ideation is detected, someone on shift needs telling immediately - not when the note is next opened.
- **`risk.py` is lexical.** It handles the phrasings in the twelve public cases. Paraphrases with no shared vocabulary would be missed. This is the largest unknown in the system.
- **The default diagnosis and medication are still emitted** by the deterministic provider. Surfaced in `unsupported_or_uncertain_items` and caught by `make evaluate`, but not removed.
- **Latency is unmeasured under load.** No test at the 20-concurrent burst. Timeouts in `models.json` (20s, 30s) sit above the 8s p95 target, so a slow call can blow the SLO and still log as a success.
- **No auth or TLS on the endpoint.** Fine for local synthetic data, blocking for anything else. See `THREAT.md`.

## Example request

```bash
curl -s http://127.0.0.1:8080/v1/clinical-notes \
  -H 'Content-Type: application/json' \
  -d '{"encounter_id":"demo-1","transcript":"The synthetic patient reports sleeping poorly and denies current suicidal thoughts.","intake":{},"note_format":"structured"}'
```