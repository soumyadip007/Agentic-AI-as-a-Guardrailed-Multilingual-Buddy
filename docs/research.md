# Research Context

## Paper-2 positioning (this repo)

**TL-Guard** is an agentic multilingual buddy with:

1. Closed loop Perceive → Decide → Act → Reflect → Remember
2. Fixed **Scaffold Map** (self-guardrails)
3. **Context-grounded Act** (local KB retrieve)
4. Translanguaging-aware intent + disclosure

It is **not** an EduHarness extension. Shared ideas (disclosure, pedagogical safety) may inform design; there is no code dependency. Novelty is **not** a teacher-configurable LSM harness UI.

## Research questions (aligned)

- RQ1: Can a deliberative agent support legitimate translanguaging while preventing cross-lingual leakage under a frozen Scaffold Map?
- RQ2: Does context-grounded Act improve factual alignment without collapsing scaffold integrity?
- RQ3: How well does heuristic intent separate clarification from adversarial switching?

## Evaluation sketch

- Scaffold Map compliance $C$ over matrix cells
- Retrieval hit rate on seeded concepts
- End-to-end legitimate / adversarial trajectories
- Planned: classroom IRB, intent F1, mastery gain, false suppression

See [paper.md](paper.md) for the full write-up.
