# HTTP API

Base: `http://127.0.0.1:8000`

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | Liveness |
| GET | `/courses` | List courses from Scaffold Maps |
| POST | `/sessions` | Body: `{course_id, concept}` |
| GET | `/sessions/{id}` | Session state |
| POST | `/sessions/{id}/turns` | Body: `{message}` → `TurnRecord` |
| GET | `/scaffold-maps/{course_id}` | **Read-only** Scaffold Map |
| GET | `/policies/{course_id}` | Alias of Scaffold Map (read-only) |
| GET | `/audit` | Research audit log |
| GET | `/escalations` | Alias of `/audit` |

There is **no** `PUT /policies` — Scaffold Maps are not teacher-editable via API.

Turn metadata may include `context_sources` from KB retrieval.
