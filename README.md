# TL-Guard

**Agentic multilingual buddy with fixed self-guardrails and context-grounded Act.**

TL-Guard is an **agent**, not a chatbot wrapper and not a teacher policy harness. Safety lives inside:

**Perceive → Decide → Act → Reflect → Remember**

- **Decide** uses a frozen **Scaffold Map** (language × scaffold matrix).
- **Act** retrieves local curriculum snippets, then calls the LLM (Ollama) as a tool.
- **Reflect** rewrites or blocks unsafe drafts; events go to a research audit log (no teacher console).

## Documentation (MkDocs)

```bash
pip install -e ".[docs]"
mkdocs serve -a 127.0.0.1:8001
```

Open **http://127.0.0.1:8001**.

## Features

- Multilingual + code-mixed language detection (en / hi / bn / es / mixed)
- Intent classification (legitimate translanguaging vs adversarial switching)
- Frozen Scaffold Map + disclosure contracts (Decide)
- Context-grounded Act: lexical retrieve from `data/kb/` → constrained LLM
- Reflect: leakage / over-scaffold rewrite or block
- Student-only Streamlit buddy + FastAPI
- Ollama by default; optional OpenAI

## Quick start (local)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
cp .env.example .env

ollama pull llama3
tl-guard doctor

tl-guard demo
streamlit run ui/app.py
uvicorn api.main:app --reload --port 8000
mkdocs serve -a 127.0.0.1:8001
```

## Deploy with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

- API: http://127.0.0.1:8000
- UI: http://127.0.0.1:8501
- Docs: http://127.0.0.1:8001

See [docs/deployment.md](docs/deployment.md).

## Layout

```
src/tl_guard/   TLGuardAgent (Perceive→Decide→Act→Reflect→Remember)
api/            FastAPI
ui/             Streamlit student buddy
configs/        scaffold_map_*.yaml (frozen)
data/kb/        Curriculum markdown for Act retrieval
docs/           MkDocs sources
docker-compose.yml
plan.md
```

## Tests

```bash
pytest -q
```

## Relation to EduHarness

Independent codebase. Shared research ideas may inform design; **no** code or runtime dependency on EduHarness. Novelty is agentic self-guardrailing + translanguaging + context-grounded Act — not a teacher LSM harness.
