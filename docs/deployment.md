# Deployment

## Docker Compose

Services: API (`:8000`), Streamlit UI (`:8501`), MkDocs (`:8001`).

```bash
cp .env.example .env
docker compose up --build
```

Point `TL_GUARD_OLLAMA_BASE_URL` at host Ollama (`http://host.docker.internal:11434` on Docker Desktop).

## What ships

- Student buddy only (no teacher console container role).
- Scaffold Map YAML baked into the image via `configs/`.
- KB under `data/kb/` for Act retrieval — ensure Compose volumes include `data/` if you edit KB live.

## Health

- API: `GET /health`
- CLI: `tl-guard doctor`
