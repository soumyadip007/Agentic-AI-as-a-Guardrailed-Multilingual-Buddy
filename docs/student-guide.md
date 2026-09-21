# Student Guide

## What is TL-Guard?

TL-Guard is your multilingual tutoring buddy. It helps you learn concepts in Python, math, and science — and you can ask questions in **English, Hindi, Bengali, Spanish, or any mix of these languages**. The system is designed to support your natural language mixing (translanguaging), not punish it.

But TL-Guard is not a regular chatbot. It will not just give you the answer. It follows a teacher-defined policy that controls *how much help* you get, *in which language*, to make sure you actually learn.

---

## How to Use It

### Starting a session

1. Open the UI: `streamlit run ui/app.py`
2. In the sidebar, make sure **Student** is selected.
3. Pick a **course** (e.g., "Intro to Python").
4. Type a **concept** you want to study (e.g., "loops", "functions", "variables").
5. Click **Start new session**.

### Chatting

Type your question in the chat input at the bottom. You can use:

- Pure English: "How does a for loop work?"
- Pure Hindi: "लूप क्या होता है?"
- Pure Bengali: "লুপ কী?"
- Hinglish: "Please samjhao loops ka matlab"
- Spanish: "Explícame los bucles"
- Any combination

The buddy responds in the language you used (or the closest authorized language).

---

## What You See Under Each Response

After each assistant reply, you will see metadata:

| Label | Meaning |
|---|---|
| **tier T1** | You got a hint (minimal help) |
| **tier T2** | You got a conceptual explanation |
| **tier T3** | You got a worked example |
| **tier T4** | You got a full solution (rare, usually restricted) |
| **lang en/hi/bn/es/mixed** | The language the buddy responded in |
| **outcome safe** | The response passed all safety checks |
| **outcome rewrite** | The AI originally over-shared and the response was trimmed |
| **outcome escalate** | The response was flagged for teacher review |
| **outcome block** | The request was declined with an explanation |

### Session Panel (right side)

- **Mastery**: Your estimated understanding of the concept (0–100%). Starts at 30% and updates based on your interactions.
- **Languages used**: All languages you have used in this session.
- **Turns**: How many messages you have exchanged.
- **Notes**: System reasoning — why a particular decision was made.

---

## Why Can't I Get the Full Answer?

Your teacher has configured a **Language–Scaffold Matrix** that limits what help levels are available. This is not to frustrate you — it is to help you learn by working through problems, not just copying answers.

If you ask for a full solution and the policy does not allow it:

- The buddy will give you the highest help level it can (maybe a worked example or explanation).
- The message will be friendly and encouraging, never punitive.
- You are always welcome to ask in a different way or a different language.

---

## What Happens If You Try to Game the System?

If you switch languages specifically to extract an answer that was withheld (e.g., asking for hints in English, then switching to Hindi and demanding the full solution), TL-Guard may:

1. Tighten your help level to T1 (hints only)
2. Escalate the turn to a teacher for review
3. Block the response entirely (depending on teacher policy)

You will still receive a helpful message — TL-Guard never silently ignores you or gives an error.

---

## CLI Alternative

If you prefer a terminal:

```bash
tl-guard chat --course-id python_intro --concept loops
```

Type `/quit` to exit. The same agent loop runs underneath.
