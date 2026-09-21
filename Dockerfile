# TL-Guard agent — multi-stage image for API, UI, or docs
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY api ./api
COPY ui ./ui
COPY configs ./configs
COPY docs ./docs
COPY mkdocs.yml ./

RUN pip install --no-cache-dir -e ".[docs]"

ENV PYTHONUNBUFFERED=1 \
    TL_GUARD_LLM=ollama \
    TL_GUARD_MODEL=llama3 \
    TL_GUARD_OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    TL_GUARD_OLLAMA_TIMEOUT=120

EXPOSE 8000 8501 8001

# Default: FastAPI agent API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
