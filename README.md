# Lavni Clinical AI Reliability Challenge — Starter Repository

This repository is a deliberately incomplete prototype for the Lavni candidate assessment. All included records are synthetic.

Read the separate assessment brief before beginning. You may refactor or replace any implementation detail, but preserve the HTTP contract:

- `GET /health`
- `POST /v1/clinical-notes`

## Requirements

- Python 3.11 or newer
- No third-party Python packages are required for the starter implementation

## Run locally

```bash
make run
```

The service listens on `http://127.0.0.1:8080` by default. Override the port with `PORT`.

## Run starter tests

```bash
make test
```

## Run the starter evaluation

```bash
make evaluate
```

## Example request

```bash
curl -s http://127.0.0.1:8080/v1/clinical-notes \
  -H 'Content-Type: application/json' \
  -d '{"encounter_id":"demo-1","transcript":"The synthetic patient reports sleeping poorly and denies current suicidal thoughts.","intake":{},"note_format":"structured"}'
```

The starter tests are not a complete specification. Your submission will be evaluated against unseen synthetic cases.
