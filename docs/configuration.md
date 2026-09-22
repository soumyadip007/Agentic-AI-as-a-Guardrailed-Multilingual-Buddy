# Configuration: Scaffold Map and Knowledge Base

TL-Guard uses two fixed artifacts (not teacher-edited at runtime):

1. **Scaffold Map** — `configs/scaffold_map_{course_id}.yaml`
2. **Curriculum KB** — `data/kb/{course_id}/{concept}.md`

## Scaffold Map

Example (`scaffold_map_python_intro.yaml`):

```yaml
course_id: python_intro
name: Intro to Python
default_language: en
languages: [en, hi, bn, es, mixed]
tiers: [T1, T2, T3, T4]
topics: [variables, loops, functions, lists, conditionals]
matrix:
  en: { T1: true, T2: true, T3: true, T4: false }
  hi: { T1: true, T2: true, T3: false, T4: false }
  # ...
escalation:
  on_adversarial_intent: tighten   # tighten | block | warn
  on_leakage: rewrite              # rewrite | block
  on_policy_violation: rewrite
```

Load in code:

```python
from tl_guard.config_loader import load_scaffold_map
from tl_guard.decide.scaffold_map import ScaffoldMap

cfg = load_scaffold_map("python_intro")
buddy = ScaffoldMap(cfg)
```

`GET /scaffold-maps/{course_id}` is **read-only**. There is no `PUT` policy editor in the product API.

Legacy `lsm_*.yaml` filenames still load if a `scaffold_map_*.yaml` is missing.

## Knowledge base

Place short markdown notes under `data/kb/{course_id}/`. Act retrieves top chunks by lexical overlap with the student query + concept.

```
data/kb/python_intro/loops.md
data/kb/python_intro/variables.md
...
```

The student UI shows **Sources used** per turn when retrieval hits.

## Scaffold tiers

| Tier | Meaning |
|---|---|
| T1 | Hint / nudge |
| T2 | Conceptual explanation |
| T3 | Worked example |
| T4 | Full solution |

## Environment

See `.env.example`: `TL_GUARD_LLM`, `TL_GUARD_MODEL`, `TL_GUARD_OLLAMA_BASE_URL`, optional OpenAI keys.
