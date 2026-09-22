# Install & Run

## Prerequisites

- **Python 3.11+**
- **[Ollama](https://ollama.com)** installed and running — this is TL-Guard's default LLM backend (runs locally, no API key needed)
- At least one Ollama model pulled (e.g., `llama3`)

## Step 1: Clone and set up the environment

```bash
cd Agentic-AI-as-a-Guardrailed-Multilingual-Buddy
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev,docs]"
```

This installs TL-Guard as an editable package with the agent, API, UI, test suite, and MkDocs docs.

## Step 2: Configure the LLM

```bash
cp .env.example .env
```

The default `.env` points to Ollama:

```env
TL_GUARD_LLM=ollama
TL_GUARD_MODEL=llama3
TL_GUARD_OLLAMA_BASE_URL=http://127.0.0.1:11434
```

Make sure Ollama is running and has a model:

```bash
ollama serve           # if not already running
ollama pull llama3     # if you have not pulled it yet
```

## Step 3: Verify everything works

```bash
tl-guard doctor
```

This command:

1. Prints your configured provider, model, and Ollama URL
2. Lists models available on your Ollama instance
3. Sends a one-sentence probe to verify the LLM responds

You should see **doctor: OK** with a short response from the model.

## Step 4: Run

=== "Streamlit UI (student buddy)"

    ```bash
    streamlit run ui/app.py
    ```

    Opens at `http://localhost:8501`. Student-only buddy with Sources used from KB retrieval.

=== "CLI demo"

    ```bash
    tl-guard demo
    ```
    
    Runs a scripted three-turn demo: English question → Hindi clarification → adversarial extraction attempt.

=== "Interactive CLI chat"

    ```bash
    tl-guard chat --course-id python_intro --concept loops
    ```

=== "HTTP API"

    ```bash
    uvicorn api.main:app --reload --port 8000
    ```
    
    OpenAPI docs at `http://127.0.0.1:8000/docs`.

=== "Documentation site"

    ```bash
    mkdocs serve -a 127.0.0.1:8001
    ```

## Step 5: Run tests

```bash
pytest -q
```

Tests use a test-only FakeLLM (injected via `TLGuardAgent(llm=FakeLLM())`). Production code always calls Ollama or OpenAI.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `LLMError: Cannot reach Ollama` | Run `ollama serve`. Check the URL in `.env`. |
| Model not found | `ollama pull llama3` (or set `TL_GUARD_MODEL` to a model you have). |
| Very slow first response | Normal — Ollama loads model weights into memory on first call. Subsequent calls are fast. |
| `ModuleNotFoundError` | Activate `.venv` and re-run `pip install -e ".[dev,docs]"`. |

Next: [Local LLM (Ollama)](llm-ollama.md) for backend details, or jump to the [Complete workflow](workflow.md).
