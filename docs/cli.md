# CLI Reference

TL-Guard ships a `tl-guard` command-line tool (built with Typer).

---

## Commands

### `tl-guard doctor`

Verify that the LLM backend is reachable and working.

```bash
tl-guard doctor
```

What it does:
1. Prints the configured provider, model, and Ollama URL
2. Calls Ollama's `/api/tags` to list available models
3. Sends a one-sentence probe completion
4. Prints **OK** or **FAILED** with an error message

Run this after installation to verify your setup.

---

### `tl-guard courses`

List all available LSM course policies:

```bash
tl-guard courses
```

Output:
```
┌────────────────────┬──────────────────┐
│ course_id          │ name             │
├────────────────────┼──────────────────┤
│ general_science    │ General Science  │
│ linear_algebra     │ Linear Algebra   │
│ python_intro       │ Intro to Python  │
└────────────────────┴──────────────────┘
```

---

### `tl-guard preview`

Show what the LSM authorizes for a given language and mastery level:

```bash
tl-guard preview --language hi --mastery 0.3 --course-id python_intro
```

Output:
```
╭──────── LSM Preview ────────╮
│ Course: Intro to Python     │
│ Language: hi                │
│ Mastery: 0.3               │
│ Max authorized: T2          │
│ Selected tier: T2           │
│ Authorized: True            │
╰─────────────────────────────╯
```

Options:
- `--language` — Student language code (en, hi, bn, es, mixed)
- `--mastery` — Float 0–1
- `--course-id` — Course identifier
- `--tier` — Override desired tier (T1–T4) instead of auto-selecting

---

### `tl-guard chat`

Interactive tutoring session in the terminal:

```bash
tl-guard chat --course-id python_intro --concept loops
```

Type messages in any supported language. Each response shows detected language, tier, intent, outcome, and mastery. Type `/quit` to exit.

---

### `tl-guard demo`

Run a scripted three-turn demo showing the guardrail behavior:

```bash
tl-guard demo --course-id python_intro
```

The demo sends:
1. An English question about for loops (→ T3 worked example)
2. A Hindi/mixed clarification request (→ T2 explanation, legitimate intent)
3. An adversarial "FULL SOLUTION PLEASE पूरा कोड दे दो" (→ T1 hint + escalation)

Outputs the full JSON trace of all three turns.
