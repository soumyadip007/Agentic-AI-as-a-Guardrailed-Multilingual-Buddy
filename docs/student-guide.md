# Student guide

## Open the buddy

```bash
source .venv/bin/activate
streamlit run ui/app.py
```

In the sidebar, choose **Student**.

## Start a session

1. Pick a **course** (e.g. Intro to Python).  
2. Set a **concept** (e.g. `loops`).  
3. Click **Start new session**.  

## Chat in any supported language

You may write in:

- English  
- Hindi (Devanagari)  
- Bengali  
- Spanish  
- Mixed / Hinglish  

Translanguaging is welcome. The buddy will not punish language mixing.

## What the UI shows

Under each assistant message you may see:

- **tier** — help level used (T1 hint … T4 full solution)  
- **lang** — response language  
- **outcome** — `safe` / `rewrite` / `escalate` / `block`  

The right **Session panel** shows mastery, languages used, and policy notes.

## What to expect when asking for answers

If you switch language mainly to extract a full solution that was withheld earlier, TL-Guard may:

- give only a short hint (T1),  
- rewrite an over-complete model reply, or  
- escalate to a teacher for review — while still offering a learning-oriented message.

## CLI alternative

```bash
tl-guard chat --course-id python_intro --concept loops
```

Type `/quit` to leave.
