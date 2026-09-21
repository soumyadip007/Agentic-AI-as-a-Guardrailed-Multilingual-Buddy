# Teacher Guide: Configuring TL-Guard

As a teacher, you control what help TL-Guard gives students, in which languages, and what happens when the system detects problems. You do this through the **Language–Scaffold Matrix (LSM)**.

---

## The Language–Scaffold Matrix (LSM)

The LSM is a policy table. Each cell answers: "Can a student receive this level of help in this language?"

### The Four Help Levels (Scaffold Tiers)

| Tier | Name | What the student receives | Example |
|------|------|--------------------------|---------|
| **T1** | Nudge / Hint | A short pointer without revealing the answer | "Think about what happens when the counter reaches zero." |
| **T2** | Conceptual explanation | A paragraph explaining the idea in the student's terms, without code or a worked solution | "A for loop repeats a block of code once for each item in a sequence." |
| **T3** | Worked example | Step-by-step walkthrough showing the key logic, but leaving the final step for the student | "Step 1: Create a list. Step 2: Write `for item in list:`. Step 3: Inside the loop... now you complete it." |
| **T4** | Full solution | Complete code or complete answer | Rarely authorized. Usually disabled or English-only. |

### Example LSM for "Intro to Python"

|  | T1 (Hint) | T2 (Explanation) | T3 (Worked example) | T4 (Full solution) |
|---|:-:|:-:|:-:|:-:|
| **English** | ✅ | ✅ | ✅ | ❌ |
| **Hindi** | ✅ | ✅ | ❌ | ❌ |
| **Bengali** | ✅ | ✅ | ❌ | ❌ |
| **Spanish** | ✅ | ✅ | ✅ | ❌ |
| **Mixed/Hinglish** | ✅ | ✅ | ❌ | ❌ |

What this means in practice:
- A student asking in Hindi can get hints and explanations, but not worked examples.
- If they want a worked example, the system responds in English (where T3 is allowed).
- Nobody gets a full solution (T4) in any language.

---

## How to Edit the LSM

### Method 1: UI (Recommended)

1. Open `streamlit run ui/app.py`.
2. In the sidebar, switch to **Teacher**.
3. Select the **LSM Editor** tab.
4. Choose a course from the dropdown.
5. You will see the matrix displayed as checkboxes: one row per language, one column per tier.
6. Toggle checkboxes to allow or deny each combination.
7. Set escalation behavior (see below).
8. Click **Save matrix from checkboxes**.

Changes take effect immediately on the next student turn.

### Method 2: YAML (advanced)

The same tab has a YAML text area showing the raw config. You can edit directly:

```yaml
matrix:
  en:   { T1: true, T2: true, T3: true,  T4: false }
  hi:   { T1: true, T2: true, T3: false, T4: false }
  bn:   { T1: true, T2: true, T3: false, T4: false }
  es:   { T1: true, T2: true, T3: true,  T4: false }
  mixed:{ T1: true, T2: true, T3: false, T4: false }
```

Click **Save from YAML**.

### Method 3: Edit files on disk

Files are in `configs/`:

- `lsm_python_intro.yaml`
- `lsm_linear_algebra.yaml`
- `lsm_general_science.yaml`

---

## Escalation Settings

Below the matrix, you configure what happens in two scenarios:

### On adversarial intent

When TL-Guard detects that a student switched languages specifically to extract an answer:

| Option | What happens |
|---|---|
| **warn** | Log the event but continue with the same tier |
| **tighten** | Drop the scaffold tier by one level (e.g., T2 → T1) |
| **escalate** | Respond with a safe T1 hint AND queue an item for you in the Escalations tab |
| **block** | Do not respond. Show a non-punitive refusal and queue for your review |

### On leakage detection

When the post-check detects the LLM over-disclosed (gave more than authorized):

| Option | What happens |
|---|---|
| **rewrite** | Automatically strip the response down to the authorized tier |
| **escalate** | Rewrite AND queue for your review |
| **block** | Do not show the response. Show a refusal |

---

## The Escalations Tab

When turns are escalated, they appear in **Teacher Console → Escalations**:

Each item shows:

- **Reason**: Why it was escalated (e.g., "adversarial intent → teacher escalation", "consecutive rewrites")
- **Student message**: Exactly what the student typed
- **Draft response**: The LLM's original output (before rewriting)
- **Recommended action**: What TL-Guard suggests (e.g., "review and confirm scaffold tier")

You can:

- Add a resolution note
- Click **Resolve** to dismiss

If a student triggers two consecutive rewrites, TL-Guard auto-escalates even without adversarial intent, so you can investigate whether the LLM is systematically ignoring tier constraints for that concept.

---

## Preview

At the bottom of the LSM Editor, a **Preview** section lets you test: "For language X, what is the maximum authorized tier?" This helps verify your policy before students interact with it.

CLI equivalent:

```bash
tl-guard preview --language hi --mastery 0.3 --course-id python_intro
```

---

## Pedagogy Reminder

TL-Guard is built on García et al.'s (2017) translanguaging framework. The key insight: **language mixing is a learning resource, not a misbehavior.** When configuring the LSM:

- **Allow** T1–T2 in home languages (Hindi, Bengali) so students can use their full linguistic repertoire for understanding.
- **Restrict** T3–T4 to English (or the language of instruction) if you want students to engage with technical content in the target language.
- **Never** set all tiers to false for a language — always leave at least T1 so students get a helpful response.
