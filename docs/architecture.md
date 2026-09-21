# Architecture overview

## Package layout

```
src/tl_guard/
  perceive/     # language, mastery, intent, session
  decide/       # LSM, scaffold, language, disclosure
  act/          # Ollama/OpenAI executor, rewriter, refusal
  reflect/      # post-check, leakage, escalation
  remember/     # session updater
  pipeline/     # verify → LLM → post-check → output
  agent.py      # orchestrator
  settings.py   # env config
api/            # FastAPI
ui/             # Streamlit student + teacher
configs/        # LSM YAML
docs/           # MkDocs sources
```

## Agentic loop (not a multi-agent swarm)

| Step | Responsibility |
|------|----------------|
| **Perceive** | Languages, mastery (BKT), switch intent |
| **Decide** | LSM + disclosure contract → plan |
| **Act** | Constrained generation via Ollama |
| **Reflect** | Leakage / scaffold post-check; escalate |
| **Remember** | Persist session for the next turn |

## Harness pipeline

Independent of EduHarness. Own path:

```
Student → verify → LLM (Ollama) → post-check → output
```

## Key types

- `ScaffoldTier` — T1…T4  
- `LanguageIntent` — legitimate / adversarial / neutral / none  
- `PolicyOutcome` — safe / rewrite / escalate / block / tighten  
- `GenerationPlan` — authorized tier + response language  
- `TurnRecord` — full audited turn  

Defined in `src/tl_guard/models.py`.
