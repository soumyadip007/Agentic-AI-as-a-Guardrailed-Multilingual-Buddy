# TL-Guard Home

TL-Guard is a **guardrailed multilingual tutoring agent** — a student buddy that supports translanguaging while **self-regulating** how much help to give, and **grounding** answers in local curriculum context.

"Guardrailed" means pedagogical safety: preventing answer dumps, scaffolding collapse, and cross-lingual leakage — enforced by a fixed **Scaffold Map**, not a live teacher policy console.

## The agent loop

**Perceive → Decide → Act → Reflect → Remember**

| Stage | What happens |
|---|---|
| **Perceive** | Detect language / code-mixing, update BKT mastery, classify switch intent |
| **Decide** | Clamp scaffold tier and response language under the frozen Scaffold Map |
| **Act** | Retrieve curriculum snippets from `data/kb/`, then call the LLM with a constrained prompt |
| **Reflect** | Post-check for leakage / over-disclosure; rewrite or block; audit if needed |
| **Remember** | Persist turn, mastery, languages used, retrieval sources |

The LLM is only a **tool inside Act**.

## Novelty (research angle)

1. Single deliberative agent (not a RAG chatbot wrapper).
2. Fixed Scaffold Map — self-guardrails without a teacher harness UI.
3. Context-grounded Act under translanguaging-aware disclosure.

Independent of EduHarness (no code dependency).

## Quick links

| Goal | Doc |
|---|---|
| Install and run | [Getting started](getting-started.md) |
| Understand the loop | [Workflow](workflow.md) · [Architecture](architecture.md) |
| Scaffold Map + KB | [Configuration](configuration.md) |
| Student UX | [Student guide](student-guide.md) |
| Research / paper | [Research](research.md) · [Paper](paper.md) |
| HTTP API | [API](api.md) |

```bash
streamlit run ui/app.py    # student buddy
uvicorn api.main:app --reload --port 8000
mkdocs serve -a 127.0.0.1:8001
```
