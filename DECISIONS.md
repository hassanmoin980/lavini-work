0. A model never decides risk. risk.py does that in code and quotes the sentence it found. A worse model gives worse wording, not a missed suicide risk.
1. Prompting for now. The model's job is small, that is to turn a transcript into four narrative fields. Nothing more is needed for that. Retrieval later, and it's house style we retrieve, not patient data. Eg. pull in the clinic's own note examples when consistency becomes the complaint.
2. No fine-tuning. The bugs found were related to diagnoses, missed negation and a prompt injection. Training fixes none of them. Twelve public cases is not a training set. Anything trained on it would overfit. Moreover, a fine-tuned model becomes a PHI-bearing artifact with its own retention, deletion and memorisation problems. Big permanent cost for a problem we haven't confirmed.
3. Schema validation, injection detection, leakage checks are done through code only (deterministic).
4. Writing the note on a low-risk session can be done via small open-weight model. 
5. Any risk found will be routed to the strongest configured model.
6. Cost routing applies only where no risk was found. Never route risk down to save money.
7. Human review on every note, no exceptions.
8. evaluation returns one of three outcomes: unsafe, needs work, or acceptable as a clinician-reviewed draft.
9. Safety failures aren't tradeable. Even one missed current risk is unsafe.
10. Add the model to app/models.json with "enabled": true in order to add / run a model.
11. A model that improves prose while regressing on schema validity or leakage does not ship.
12. config.load_models() filters the model out, so router.choose_providers() builds that provider and (in case of rollback) traffic falls to the
next tier. A disabled model never appears in the chain.
13. DeterministicProvider is always last in the chain and needs no credentials or network. There is always a floor.
14. Model versioning is good practice, which is not implemented in this case.
15. No training / fine-tuning happening.
16. Any third party touching the data needs to have a signed BAA.
17. Data versioning required, so any trained model traces back to the exact snapshot it saw. Currently not implemented.
18. Removing PHI first is necessary but not sufficient. De-identification is not a licence to train.
19. De-identification cleans the input; memorisation works on whatever was in the input. Currently not being implemented.
20. base_url points at the Hugging Face router, which fans requests to whichever partner it picks. We can't sign a BAA with a party we don't know in advance.
21. Need a named provider - dedicated endpoint or self-hosted. Both speak the same protocol, so it's one line in models.json and no code change.
22. Signed BAA and zero retention in writing. "They probably delete it" isn't a control.
23. Redact before the transcript leaves our network where a hosted model is unavoidable - but treat redacted text as PHI anyway for access, retention and audit.
24. Encrypted in transit and at rest, keys we hold. Secrets in a manager with rotation. The .env file is a dev convenience, not key management.
25. No PHI in logs, traces, caches, error bodies or support tools. 
26. For training: all the above, plus training runs on our own infrastructure against a versioned snapshot, and the memorisation tests pass before the model serves anything.
27. A model is not HIPAA compliant. The environment around it can be - network path, retention, access control, audit trail, deletion, and the clinician reading the draft.
28. Whether clinicians find the drafts useful. No metric answers that; it needs real notes in front of real reviewers. It also needs an evaluation criteria to evaluate it.
29. Need to create an ops pipeline that can detect and automatically add multiple risky phrases in the corpus automatically.