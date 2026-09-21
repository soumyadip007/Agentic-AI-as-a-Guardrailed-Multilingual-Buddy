# CLI reference

Entry point: `tl-guard` (Typer).

| Command | Description |
|---------|-------------|
| `tl-guard doctor` | Verify Ollama/OpenAI and probe a completion |
| `tl-guard courses` | List LSM course policies |
| `tl-guard preview` | Show authorized tier for language + mastery |
| `tl-guard chat` | Interactive tutoring session |
| `tl-guard demo` | Scripted En→Hi→adversarial demo |

## Examples

```bash
tl-guard doctor

tl-guard preview --language bn --mastery 0.5 --course-id general_science

tl-guard chat --course-id linear_algebra --concept vectors

tl-guard demo --course-id python_intro
```

Source: `src/tl_guard/cli.py`.
