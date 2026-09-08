## Where PHI can end up 

1. Prompts: The transcript goes to whatever partner the HF router picks. We can't sign a BAA with a party we don't know in advance. Preferably need a dedicated endpoint or a self-hosted model.

2. Outputs: The note copies the transcript straight into subjective instead of summarising it. So the note carries every identifier the source did.

3. Logs: Handled. We log encounter id, model, latency and outcome - never content.

4. Traces: When we add tracing, spans must carry ids and timings only.

5. Caches: If we add a response cache, key on a hash of the transcript and store only the note id. Never the transcript itself, and never in a shared cache.

6. Backups: Backups of the notes store are PHI and inherit the same retention and access rules for all PHI data. They also break deletion, a restore can resurrect a record a patient asked us to remove, so deletion has to reach backups or the retention window has to be short enough that it doesn't matter.

7. Support tooling: Right now anyone with database or log access can read transcripts, which in practice means support and on-call developers. Support should see
metadata and error references by default, with transcript access separately requested, time-boxed and logged. Introducing RBAC may help.

## Controls

8. Provider retention: Need zero retention in writing from the provider (if online model used), in the contract. "They probably delete it" isn't a control, and a
privacy page isn't a commitment

9. Encryption and key management: Need TLS in transit, encryption at rest, and keys we hold and rotate. Keys currently sit in a plaintext .env file. Needs a secrets manager with rotation and access logging.

10. Least privilege: There's no auth on the endpoint at all. Anyone who can reach the port can post transcripts and read notes back. Needs authenticated callers with scoped tokens, per-caller identity on every request, and separate roles for writing notes, reading notes, and reading transcripts (RBAC control).

11. Personal devices: Nothing stops a therapist pasting a transcript into a chat tool on their laptop, and policy alone won't stop it. Needs a sanctioned path that's easier than the workaround.

## Attacks

12. Prompt injection: Handled structurally, however, guardrails need to be implemented on a much deeper level. Risk comes from risk.py and the model only writes prose, so injected text can't move a safety field. Instruction-like text gets flagged and handled.

13. Model extraction and memorisation: Nothing is trained yet, so the only real exposure is a provider keeping our prompts, but if we do train we need to plant known strings and scan for them, feed the model the first line of a training note to see if it finishes it, and ask it outright for patient records. De-identification won't help, it cleans the input and memorisation works on whatever was in the input.

## Operations

14. Audit trail: None used right now. No model / prompt versioning. After an incident the only question that matters is which notes came from the bad model version, and we can't answer it. Needs

15. Incident response: Detection comes from the evaluation and the leakage check. Containment works today - flip "enabled": false in models.json and the router falls
through to the deterministic provider, which needs no key and no network, so there's always a floor. What doesn't work is the next step: identifying which notes were affected, because of point 14. So we can stop the bleeding but not scope the damage.

16. Deletion: Not solved. A withdrawal has to reach transcripts, notes, logs, backups, and any model trained on that data. If we can't enumerate where a record went we can't honour the request, and "we tried" isn't a defence. This is a reason to keep transcript retention short by default, the less we keep, the less we have to chase.

17. Human review: Every note is a draft and requires_human_review is set on any risk found or ungrounded content. This is the last real control and the most likely to rot. if reviewers start rubber-stamping, everything above stops mattering. Evidence quotes exist so checking a risk flag takes seconds instead of a re-read. 

18. Emergency clinical escalation: No emergency escalation. Detecting risk and telling nobody is detecting it late.
