# ARCHITECTURE
- Contract: storyboard.json + schema/storyboard.schema.json (validated at the start of every stage).
- Stages: keyframes -> shots -> music -> narration -> assemble (script is a manual drafting aid).
- Caching: each artefact is named `<shot>_<hash12>.<ext>`, hash = sha256(model, params incl. prompt+seed). Edit one prompt -> one new hash -> one model call.
- Failure handling: `common.retry` exponential backoff; stages are idempotent so a re-run resumes.
- Logging: `common.log_call` appends to runs.jsonl.
- GPU stages (Wan 2.2, ACE-Step) run in Kaggle notebooks under notebooks/; outputs are downloaded into outputs/ and consumed by shots/music.
TODO: diagram + notes after build.
