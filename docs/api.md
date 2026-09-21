# HTTP API Reference

TL-Guard exposes a REST API via FastAPI.

```bash
uvicorn api.main:app --reload --port 8000
```

Interactive OpenAPI docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Endpoints

### Health

| Method | Path | Response |
|---|---|---|
| GET | `/health` | `{"status": "ok"}` |

---

### Courses

| Method | Path | Response |
|---|---|---|
| GET | `/courses` | List of `{course_id, name, path}` for all LSM configs |

---

### Sessions

| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/sessions` | `{"course_id": "python_intro", "concept": "loops"}` | `SessionState` (session_id, course_id, concept, mastery, turns) |
| GET | `/sessions/{id}` | — | `SessionState` with all turns so far |

---

### Turns (the main interaction)

| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/sessions/{id}/turns` | `{"message": "Explain for loops"}` | `TurnRecord` |

The `TurnRecord` response contains:

```json
{
  "turn_index": 0,
  "student_message": "Explain for loops",
  "detected_language": "en",
  "intent": "none",
  "authorized_tier": "T3",
  "selected_tier": "T3",
  "response_language": "en",
  "assistant_message": "A for loop repeats...",
  "outcome": "safe",
  "mastery": 0.3,
  "notes": ["no language switch"],
  "metadata": {
    "detection_confidence": 0.99,
    "code_mixed": false,
    "intent_confidence": 0.9,
    "leakage_score": 0.0
  }
}
```

---

### Policies (teacher API)

| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/policies/{course_id}` | — | `LSMConfig` |
| PUT | `/policies/{course_id}` | `{"config": {…LSMConfig…}}` | Updated `LSMConfig` |

PUT overwrites the YAML on disk and clears the agent cache.

---

### Escalations

| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/escalations?open_only=true` | — | List of `EscalationItem` |
| POST | `/escalations/{id}/resolve` | `{"note": "reviewed, OK"}` | Resolved `EscalationItem` |

---

## Example Session

```bash
# Create a session
SID=$(curl -s -X POST http://127.0.0.1:8000/sessions \
  -H 'Content-Type: application/json' \
  -d '{"course_id":"python_intro","concept":"loops"}' | jq -r .session_id)

# Send a turn
curl -s -X POST "http://127.0.0.1:8000/sessions/$SID/turns" \
  -H 'Content-Type: application/json' \
  -d '{"message":"How do for loops work?"}' | jq .

# Check escalations
curl -s http://127.0.0.1:8000/escalations | jq .
```
