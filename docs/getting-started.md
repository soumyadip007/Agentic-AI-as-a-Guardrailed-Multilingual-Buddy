# Install & run

## Prerequisites

- Python **3.11+**
- [Ollama](https://ollama.com) installed and running
- At least one local chat model (this machine already has `llama3` and `codellama`)

## 1. Clone and create a virtualenv

```bash
cd Agentic-AI-as-a-Guardrailed-Multilingual-Buddy
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,docs]"
```

## 2. Configure environment

```bash
cp .env.example .env
```

Default `.env`:

```env
TL_GUARD_LLM=ollama
TL_GUARD_MODEL=llama3
TL_GUARD_OLLAMA_BASE_URL=http://127.0.0.1:11434
TL_GUARD_OLLAMA_TIMEOUT=120
```

## 3. Verify Ollama

```bash
ollama serve          # if not already running
ollama pull llama3    # if needed
tl-guard doctor
```

`doctor` must print **OK** and a short probe reply from the model.

## 4. Run the product surfaces

=== "UI (recommended)"

    ```bash
    streamlit run ui/app.py
    ```

    Open the Streamlit URL (usually `http://localhost:8501`).

    - **Student** — multilingual tutoring chat  
    - **Teacher** — LSM editor + escalation console  

=== "CLI"

    ```bash
    tl-guard courses
    tl-guard preview --language hi --mastery 0.3
    tl-guard chat --course-id python_intro --concept loops
    tl-guard demo
    ```

=== "API"

    ```bash
    uvicorn api.main:app --reload --port 8000
    # OpenAPI: http://127.0.0.1:8000/docs
    ```

=== "Documentation site"

    ```bash
    mkdocs serve -a 127.0.0.1:8001
    # http://127.0.0.1:8001
    ```

## 5. Run tests

```bash
pytest -q
```

Unit tests inject a **FakeLLM** (test double only). Runtime always uses Ollama/OpenAI.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Cannot reach Ollama` | Start `ollama serve`; check `TL_GUARD_OLLAMA_BASE_URL` |
| Model not listed | `ollama pull llama3` (or set `TL_GUARD_MODEL=codellama`) |
| Slow first reply | First Ollama load pulls weights into memory — wait once |
| Import errors | Activate `.venv` and re-run `pip install -e ".[dev,docs]"` |

Next: [Local LLM (Ollama)](llm-ollama.md) · [Complete workflow](workflow.md)
