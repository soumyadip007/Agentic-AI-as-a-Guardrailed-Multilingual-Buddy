# TL-Guard UI

## Run

From the repo root (after `pip install -e ".[dev,docs]"` and `tl-guard doctor`):

```bash
# Optional API
uvicorn api.main:app --reload --port 8000

# Student buddy UI (uses Ollama in-process)
streamlit run ui/app.py
```

Requires a local Ollama model (`TL_GUARD_MODEL`, default `llama3`).

The UI is **student-only**: course/concept chat, mastery panel, and Sources used from KB retrieval. There is no teacher LSM editor.

Full docs: `mkdocs serve -a 127.0.0.1:8001`
