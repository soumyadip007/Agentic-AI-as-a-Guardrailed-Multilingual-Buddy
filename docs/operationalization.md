# Translanguaging operationalization (Stance / Design / Shifts)

| Principle | Computational construct in TL-Guard |
|-----------|-------------------------------------|
| **Stance** | System prompt affirms multilingual input; language switches logged as features; no penalty for L2 |
| **Design** | Language–Scaffold Matrix (YAML) — per-language allow/deny for T1–T4 |
| **Shifts** | Per-turn Decide module: mastery + intent + LSM → tier + response language |

## Code map

| Construct | Location |
|-----------|----------|
| Stance preamble | `act/llm_executor.py` → `STANCE_PREAMBLE` |
| Design (LSM) | `configs/lsm_*.yaml`, `decide/lsm_engine.py` |
| Shifts | `decide/scaffold_selector.py`, `decide/language_selector.py`, `agent.py` |

See also [Architecture](architecture.md) and [Configuration](configuration.md).
