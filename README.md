# TL-Guard

**Agentic AI as a Guardrailed Multilingual Buddy: Translanguaging Support Under Pedagogical Safety Constraints**

Independent tutoring agent with:

**Perceive → Decide → Act → Reflect → Remember**

Teachers configure a **Language–Scaffold Matrix (LSM)** so students can translanguage safely without unrestricted answer leakage.

## Documentation (MkDocs)

```bash
pip install -e ".[docs]"
mkdocs serve -a 127.0.0.1:8001
```

Open **http://127.0.0.1:8001** for the full workflow, Ollama setup, student/teacher guides, API, and architecture.

Build static site: `mkdocs build` → `site/`.

## Features

- Multilingual + code-mixed language detection (en / hi / bn / es / mixed)
- Intent classification (legitimate translanguaging vs adversarial switching)
- LSM policy engine + disclosure contracts
- Turn pipeline: **verify → LLM → post-check → output**
- **Ollama by default** (no mock LLM); optional OpenAI
- Cross-lingual leakage rewrite + teacher escalation queue
- Student + Teacher Streamlit UI and FastAPI

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
cp .env.example .env

# Ollama must be running with a model (e.g. llama3)
ollama pull llama3
tl-guard doctor

tl-guard demo
streamlit run ui/app.py
uvicorn api.main:app --reload --port 8000
mkdocs serve -a 127.0.0.1:8001
```

Optional OpenAI: set `TL_GUARD_LLM=openai` and `OPENAI_API_KEY`.

## Layout

```
src/tl_guard/   Agent + harness
api/            FastAPI
ui/             Streamlit
configs/        LSM YAML
docs/           MkDocs sources
mkdocs.yml      Docs site config
plan.md         Development plan
```

## Tests

```bash
pytest -q
```

## License

See `LICENSE`.
