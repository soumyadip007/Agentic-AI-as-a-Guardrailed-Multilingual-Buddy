# Local LLM (Ollama)

TL-Guard runs entirely locally by default. There is **no mock LLM** and no cloud dependency. Every response comes from a real model running on your machine via [Ollama](https://ollama.com).

---

## How It Works

When TL-Guard needs to generate a tutoring response, it sends an HTTP POST to Ollama's local API:

```
POST http://127.0.0.1:11434/api/chat
```

With a system prompt (encoding the tier, language, and translanguaging stance) and the student's message. Ollama runs the model (e.g., `llama3`) locally and returns the completion. No data leaves your machine.

**Code**: `src/tl_guard/act/llm_executor.py` → `OllamaLLM`

---

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `TL_GUARD_LLM` | `ollama` | Provider selection |
| `TL_GUARD_MODEL` | `llama3` | Model name as Ollama knows it |
| `TL_GUARD_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama API URL |
| `TL_GUARD_OLLAMA_TIMEOUT` | `120` | Seconds per completion (increase for slower machines) |

Set in `.env` or as environment variables.

---

## Recommended Models

| Model | Best for | RAM needed |
|---|---|---|
| `llama3` | General multilingual tutoring (default) | ~5 GB |
| `codellama` | Code-heavy Python tutoring | ~4 GB |

Switch without changing code:

```bash
export TL_GUARD_MODEL=codellama
tl-guard doctor
```

---

## Health Check

```bash
tl-guard doctor
```

Outputs:

1. Provider, model name, Ollama URL
2. Available models on the Ollama instance
3. A probe response to confirm end-to-end connectivity

If the model you configured is not listed, it tells you to run `ollama pull <model>`.

---

## Optional: OpenAI

Set these to use a cloud model instead:

```env
TL_GUARD_LLM=openai
OPENAI_API_KEY=sk-...
TL_GUARD_MODEL=gpt-4o-mini
```

If `TL_GUARD_LLM=openai` is set but `OPENAI_API_KEY` is missing, TL-Guard falls back to Ollama (not a mock).

---

## Error Behavior

When the LLM is unreachable or fails, TL-Guard raises `LLMError` with a descriptive message:

- `Cannot reach Ollama at http://127.0.0.1:11434` → Start `ollama serve`
- `Ollama HTTP 404 for model 'llama3'` → `ollama pull llama3`
- `Ollama timed out after 120s` → Increase `TL_GUARD_OLLAMA_TIMEOUT` or check system load

There are no silent failures or fake responses.
