# Local LLM (Ollama)

TL-Guard **does not ship a mock LLM**. Generation always goes through a real model.

## Default: Ollama

| Setting | Default | Meaning |
|---------|---------|---------|
| `TL_GUARD_LLM` | `ollama` | Provider |
| `TL_GUARD_MODEL` | `llama3` | Model name as known to Ollama |
| `TL_GUARD_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama HTTP API |
| `TL_GUARD_OLLAMA_TIMEOUT` | `120` | Seconds per completion |

### Install / pull models

```bash
# ensure daemon is up
ollama serve

# recommended default for this project
ollama pull llama3

# also fine for code-heavy tutoring
ollama pull codellama
```

Switch model without code changes:

```bash
export TL_GUARD_MODEL=codellama
tl-guard doctor
```

### How calls are made

TL-Guard posts to Ollama’s chat API:

`POST {base}/api/chat` with `stream: false`, system + user messages, temperature `0.4`.

Implementation: `src/tl_guard/act/llm_executor.py` → `OllamaLLM`.

### Health check

```bash
tl-guard doctor
```

This:

1. Prints provider + model + base URL  
2. Lists models from `/api/tags`  
3. Runs a one-sentence probe completion  

## Optional: OpenAI

Only when explicitly selected:

```env
TL_GUARD_LLM=openai
OPENAI_API_KEY=sk-...
TL_GUARD_MODEL=gpt-4o-mini
```

If `TL_GUARD_LLM=openai` but no key is set, TL-Guard falls back to **Ollama** (still no mock).

## Errors you should see (by design)

Instead of silent fake answers, failures raise `LLMError`, for example:

- Ollama not running  
- Model not pulled  
- HTTP/timeout errors  

Fix the local stack, then re-run `tl-guard doctor`.
