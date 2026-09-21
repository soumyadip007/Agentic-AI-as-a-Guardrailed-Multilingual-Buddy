# TL-Guard

**Agentic AI as a Guardrailed Multilingual Buddy: Translanguaging Support Under Pedagogical Safety Constraints**

TL-Guard is an **agent**, not a chatbot wrapper. Safety lives inside the agent loop:

**Perceive → Decide → Act → Reflect → Remember**

The LLM (Ollama) is only a tool used inside **Act**. Teachers configure a **Language–Scaffold Matrix (LSM)** so students can translanguage safely without unrestricted answer leakage.

## Documentation (MkDocs)

```bash
pip install -e ".[docs]"
mkdocs serve -a 127.0.0.1:8001
```

Open **http://127.0.0.1:8001** for the full workflow, Ollama setup, student/teacher guides, API, architecture, and deployment.

Build static site: `mkdocs build` → `site/`.

## Features

- Multilingual + code-mixed language detection (en / hi / bn / es / mixed)
- Intent classification (legitimate translanguaging vs adversarial switching)
- LSM policy engine + disclosure contracts (Decide)
- Agent Act + Reflect: authorize → constrained LLM → post-check
- **Ollama by default** (no mock LLM); optional OpenAI
- Cross-lingual leakage rewrite + teacher escalation queue
- Student + Teacher Streamlit UI and FastAPI

## Quick start (local)

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

## Deploy with Docker Compose

Requires Docker and a running Ollama on the host (`http://host.docker.internal:11434`):

```bash
cp .env.example .env
docker compose up --build
```

- API: http://127.0.0.1:8000
- UI: http://127.0.0.1:8501
- Docs: http://127.0.0.1:8001

See [docs/deployment.md](docs/deployment.md).

Optional OpenAI: set `TL_GUARD_LLM=openai` and `OPENAI_API_KEY`.

## Layout

```
src/tl_guard/   TLGuardAgent (Perceive→Decide→Act→Reflect→Remember)
api/            FastAPI
ui/             Streamlit
configs/        LSM YAML
docs/           MkDocs sources
docker-compose.yml
Dockerfile
plan.md         Development plan
```

## Tests

```bash
pytest -q
```

## License

See `LICENSE`.
