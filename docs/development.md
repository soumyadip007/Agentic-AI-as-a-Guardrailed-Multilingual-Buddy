# Development Guide

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
cp .env.example .env
tl-guard doctor
pytest -q
```

---

## Tests

```bash
pytest -q
```

Unit tests inject a `FakeLLM` test double into `TLGuardAgent(llm=FakeLLM())`. The production code uses `OllamaLLM` or `OpenAILLM` — there is no mock in production.

Test coverage:
- Language detection (Hindi script, English, code-mixed)
- LSM policy enforcement
- Disclosure clamping
- Intent classification (legitimate, adversarial)
- Pipeline verify/block
- Full end-to-end translanguaging session (3 turns)
- API import check
- LLM provider defaults to Ollama

---

## Docs Site (MkDocs Material)

```bash
# Live reload while editing docs/
mkdocs serve -a 127.0.0.1:8001

# Build static site → site/
mkdocs build --clean
```

Deploy to GitHub Pages:

```bash
mkdocs gh-deploy
```

---

## LSM Policy Validation

Run the E1 consistency checker:

```bash
python experiments/e1_lsm_validation.py
```

Verifies that every language × tier combination in every LSM config is internally consistent.

---

## Project Files Reference

| File / Dir | Purpose |
|---|---|
| `src/tl_guard/` | Agent core: perceive, decide, act, reflect, remember |
| `api/main.py` | FastAPI |
| `ui/app.py` | Streamlit student + teacher UI |
| `configs/` | LSM YAML policies |
| `tests/` | pytest suite |
| `experiments/` | Research experiment scripts |
| `docs/` | MkDocs source pages |
| `mkdocs.yml` | Docs site config |
| `plan.md` | Multi-week research/engineering plan |
| `research_plans.md` | Full literature review and methodology |
