# Research Context

TL-Guard is a research artifact for the paper:

**"Agentic AI as a Guardrailed Multilingual Buddy: Translanguaging Support Under Pedagogical Safety Constraints"**

---

## The Research Problem

Multilingual students naturally mix languages when learning (translanguaging). Existing AI tutors either:

1. Support language mixing without pedagogical guardrails (KiKo-Prim, GurukulAI) — students can extract full answers by switching languages.
2. Have pedagogical guardrails but only work in English (SafeTutors, SHAPE) — multilingual students lose safety protection the moment they switch languages.
3. Treat code-switching as a security threat (MultiJail, CSRT) — they block the behavior instead of supporting it.

**The gap**: No system integrates translanguaging pedagogy theory with formal pedagogical safety constraints.

---

## Research Questions

1. **RQ1**: How can García's Stance/Design/Shifts be computationally operationalized for AI tutoring agents?
2. **RQ2**: Can a Language–Scaffold Matrix maintain pedagogical safety while supporting legitimate translanguaging?
3. **RQ3**: Can a harness pipeline distinguish legitimate translanguaging from adversarial language-switching?
4. **RQ4**: Does a guardrailed multilingual buddy improve learning outcomes vs. English-only and unguardrailed multilingual baselines?
5. **RQ5**: What are the failure modes — when does TL-Guard incorrectly suppress legitimate translanguaging?

---

## Contributions

| # | Contribution | Implementation |
|---|---|---|
| C1 | First computational operationalization of translanguaging pedagogy | See [Operationalizing translanguaging](operationalization.md) |
| C2 | Language–Scaffold Matrix (LSM) | `configs/lsm_*.yaml`, `decide/lsm_engine.py` |
| C3 | Translanguaging-aware disclosure contracts | `decide/disclosure_checker.py` |
| C4 | Language Intent Classifier | `perceive/intent_classifier.py` |
| C5 | Empirical evaluation framework | `experiments/`, `plan.md` |

---

## Literature Streams

The full literature review is in `research_plans.md` (Paper 2 section). Four areas:

1. **AI Multilingual Buddy**: KiKo-Prim, Walter, Acharjo, GurukulAI, 7S Samiti
2. **Translanguaging Theory**: García et al. (2017), García & Li Wei (2014), Cummins
3. **Pedagogical Safety**: SafeTutors, SHAPE, Auditable Release Control
4. **Guardrail Systems**: NeMo Guardrails, EvalGuard, Indian Multilingual Prompt Injection

---

## Evaluation Plan

| Experiment | Measures | Status |
|---|---|---|
| E1: LSM policy validation | 100% consistency across all configs | **Done** (60/60 passed) |
| E2: Intent classification | Precision/Recall/F1 on balanced dataset | Planned |
| E3: Comparative tutoring | Mastery gain across 4 conditions | Planned |
| E4: False suppression | False positive rate on legitimate translanguaging | Planned |
| E5: Teacher usability | SUS score for LSM configuration | Planned |

Read the full paper: [Paper](paper.md). Full methodology: `research_plans.md`.
