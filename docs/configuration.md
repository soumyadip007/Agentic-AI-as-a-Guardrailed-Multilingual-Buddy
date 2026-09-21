# Configuration (LSM & env)

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `TL_GUARD_LLM` | `ollama` | `ollama` or `openai` |
| `TL_GUARD_MODEL` | `llama3` | Model id |
| `TL_GUARD_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama host |
| `TL_GUARD_OLLAMA_TIMEOUT` | `120` | Request timeout (s) |
| `OPENAI_API_KEY` | — | Required only for OpenAI mode |
| `TL_GUARD_OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |

Copy from `.env.example`.

## LSM YAML shape

```yaml
course_id: python_intro
name: Intro to Python
default_language: en
languages: [en, hi, bn, es, mixed]
tiers: [T1, T2, T3, T4]
matrix:
  en:  { T1: true, T2: true, T3: true, T4: false }
  hi:  { T1: true, T2: true, T3: false, T4: false }
  mixed: { T1: true, T2: true, T3: false, T4: false }
escalation:
  on_adversarial_intent: escalate
  on_leakage: rewrite
  on_policy_violation: rewrite
```

Validated conceptually against `configs/lsm_schema.json` and loaded by `tl_guard.config_loader.LSMConfig`.

## Hot reload

- Teacher UI **Save** writes YAML to `configs/`.  
- API `PUT /policies/{course_id}` does the same and clears the in-memory agent cache.  
- Next student turn reloads the LSM.
