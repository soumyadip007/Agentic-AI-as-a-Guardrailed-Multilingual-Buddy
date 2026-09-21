# Teacher guide: Language–Scaffold Matrix (LSM)

## What is the LSM?

The **Language–Scaffold Matrix** tells TL-Guard which help levels are allowed in which languages.

| Tier | Meaning |
|------|---------|
| **T1** | Short nudge / hint |
| **T2** | Conceptual explanation |
| **T3** | Worked example (key steps) |
| **T4** | Full solution |

Example (Intro to Python): English may allow up to T3; Hindi/Bengali up to T2. Full solutions (T4) are off by default for programming courses.

## Edit in the UI

1. Open Streamlit → sidebar **Teacher**.  
2. Open **LSM Editor**.  
3. Select a course.  
4. Toggle checkboxes in the matrix (or edit YAML).  
5. Set escalation behaviour (adversarial intent / leakage).  
6. **Save**. New student turns pick up the policy immediately.

## Escalations

When the agent suspects answer-seeking via language switch, or repeatedly rewrites unsafe answers, it queues an item under **Escalations**.

For each item you see:

- reason  
- student message  
- draft model reply  
- recommended action  

Resolve with an optional note.

## Config files on disk

| File | Course |
|------|--------|
| `configs/lsm_python_intro.yaml` | Intro to Python |
| `configs/lsm_linear_algebra.yaml` | Linear Algebra |
| `configs/lsm_general_science.yaml` | General Science |
| `configs/escalation_policy.yaml` | Escalation thresholds |

Schema: `configs/lsm_schema.json`.

## Preview without chatting

```bash
tl-guard preview --language hi --mastery 0.3 --course-id python_intro
```

## Stance reminder

Language mixing is a **learning resource**, not an attack by default. Prefer allowing T1–T2 in home languages for clarification.
