# Research Audit Log

TL-Guard ships as a **student-only** buddy. There is no teacher LSM editor or escalation resolver UI.

For research and debugging, self-guardrail events (adversarial intent, blocks, consecutive rewrites) are written to an in-memory **audit log**:

- API: `GET /audit` (alias: `GET /escalations`)
- Code: `tl_guard.reflect.escalation.AUDIT_LOG`

Use this to analyze trajectories — not as a live teacher workflow. Scaffold Maps are edited as frozen YAML under `configs/` by researchers/developers, then restarted — not mutated mid-session via UI.
