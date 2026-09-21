# TL-Guard UI

## Run

From the repo root (after `pip install -e ".[dev,docs]"` and `tl-guard doctor`):

```bash
# Optional API
uvicorn api.main:app --reload --port 8000

# Student + Teacher UI (uses Ollama in-process)
streamlit run ui/app.py
```

Requires a local Ollama model (`TL_GUARD_MODEL`, default `llama3`).

Full docs: `mkdocs serve -a 127.0.0.1:8001`
