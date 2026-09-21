# HTTP API

Start:

```bash
uvicorn api.main:app --reload --port 8000
```

Interactive OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| GET | `/courses` | List LSM courses |
| POST | `/sessions` | Create session `{course_id, concept}` |
| GET | `/sessions/{id}` | Session state + turns |
| POST | `/sessions/{id}/turns` | `{message}` → `TurnRecord` |
| GET | `/policies/{course_id}` | Read LSM |
| PUT | `/policies/{course_id}` | Update LSM `{config: …}` |
| GET | `/escalations?open_only=true` | Teacher queue |
| POST | `/escalations/{id}/resolve` | Resolve with note |

## Example

```bash
curl -s http://127.0.0.1:8000/health

SID=$(curl -s -X POST http://127.0.0.1:8000/sessions \
  -H 'Content-Type: application/json' \
  -d '{"course_id":"python_intro","concept":"loops"}' | jq -r .session_id)

curl -s -X POST "http://127.0.0.1:8000/sessions/$SID/turns" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Explain for-loops with a small hint only"}'
```

Requires Ollama (or OpenAI) to be healthy — same as the UI.
