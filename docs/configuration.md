# Configuration Reference

TL-Guard is configured through two mechanisms: **environment variables** (for the LLM backend) and **YAML files** (for pedagogical policies).

---

## Environment Variables (.env)

Copy `.env.example` to `.env` and edit:

```env
TL_GUARD_LLM=ollama
TL_GUARD_MODEL=llama3
TL_GUARD_OLLAMA_BASE_URL=http://127.0.0.1:11434
TL_GUARD_OLLAMA_TIMEOUT=120
```

| Variable | Default | What it controls |
|---|---|---|
| `TL_GUARD_LLM` | `ollama` | LLM provider. Set to `openai` to use OpenAI instead. |
| `TL_GUARD_MODEL` | `llama3` | Model name as Ollama knows it (`llama3`, `codellama`, etc.) |
| `TL_GUARD_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Where your Ollama daemon is running |
| `TL_GUARD_OLLAMA_TIMEOUT` | `120` | Seconds before a request times out (models can be slow on first load) |
| `OPENAI_API_KEY` | (none) | Required only if `TL_GUARD_LLM=openai` |
| `TL_GUARD_OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |

These are loaded by `src/tl_guard/settings.py` using pydantic-settings.

---

## LSM YAML Files

Located in `configs/`. Each file defines the policy for one course.

### Full annotated example

```yaml
# Unique identifier for this course (used in API and UI)
course_id: python_intro

# Human-readable name (shown in the UI dropdown)
name: Intro to Python

# Description (shown in the Teacher Console)
description: >
  Pedagogical policy for introductory Python tutoring
  with controlled translanguaging.

# Default response language when the student's language
# is not in the matrix
default_language: en

# All supported languages for this course
languages: [en, hi, bn, es, mixed]

# Tiers available (always T1–T4, but listed for schema validation)
tiers: [T1, T2, T3, T4]

# Curriculum topics (informational; not yet enforced per-topic)
topics:
  - variables
  - loops
  - functions
  - lists
  - conditionals

# The matrix: for each language, which tiers are allowed?
matrix:
  en:
    T1: true     # hints
    T2: true     # explanations
    T3: true     # worked examples
    T4: false    # full solutions — NOT allowed
  hi:
    T1: true
    T2: true
    T3: false    # Hindi caps at explanation
    T4: false
  bn:
    T1: true
    T2: true
    T3: false
    T4: false
  es:
    T1: true
    T2: true
    T3: true     # Spanish allows worked examples
    T4: false
  mixed:
    T1: true
    T2: true
    T3: false
    T4: false

# What to do when problems are detected
escalation:
  on_adversarial_intent: escalate   # warn | tighten | escalate | block
  on_leakage: rewrite               # rewrite | escalate | block
  on_policy_violation: rewrite       # rewrite | escalate | block
```

### How the matrix is read

When the agent decides `(language=hi, tier=T3)`, it looks up `matrix.hi.T3`. If `false`, the tier is **clamped** to the highest authorized tier for that language. In this case, Hindi's max is T2, so the student gets a T2 response.

### Hot reload

When a teacher saves via the UI or `PUT /policies/{course_id}`, the YAML file is overwritten on disk and the in-memory agent cache is cleared. The next student turn loads the updated policy.

---

## Escalation Policy (configs/escalation_policy.yaml)

```yaml
name: default_escalation
thresholds:
  adversarial_confidence: 0.65
  leakage_score: 0.5
  over_disclosure_markers: 2
actions:
  warn: Log and continue with same tier
  tighten: Drop authorized scaffold tier by one level
  rewrite: Rewrite response to authorized tier
  escalate: Queue for teacher review
  block: Withhold response and request teacher review
teacher_queue:
  auto_escalate_after_consecutive_rewrites: 2
```

---

## JSON Schema (configs/lsm_schema.json)

Validates the structure of LSM YAML files. Key constraints:

- `course_id` and `name` are required strings
- `languages` must be a non-empty array
- `matrix` entries must have T1–T4 boolean fields
- `escalation` actions must be one of the allowed values
