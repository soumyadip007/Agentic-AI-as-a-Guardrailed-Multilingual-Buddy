# Development

```bash
pip install -e ".[dev,docs]"
pytest -q
mkdocs serve -a 127.0.0.1:8001
```

## Module map

| Concern | Path |
|---|---|
| Agent loop | `src/tl_guard/agent.py` |
| Scaffold Map | `src/tl_guard/decide/scaffold_map.py`, `configs/scaffold_map_*.yaml` |
| Retriever | `src/tl_guard/act/retriever.py`, `data/kb/` |
| Act+Reflect | `src/tl_guard/pipeline/turn_pipeline.py` |
| UI | `ui/app.py` |
| API | `api/main.py` |

## Adding a course

1. Add `configs/scaffold_map_{id}.yaml` with matrix + topics.
2. Add `data/kb/{id}/*.md` concept notes.
3. Restart API/UI; `list_courses()` picks it up.

## Tests

`tests/test_core.py` uses `FakeLLM` and exercises Scaffold Map, retrieval, and translanguaging e2e. Prefer FakeLLM in unit tests — never ship a mock as the production backend.
