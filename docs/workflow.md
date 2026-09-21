# Complete Workflow: What Happens When a Student Sends a Message

This page traces the exact path a single student message takes through TL-Guard, from the moment the student types to the moment they see a response — and potentially the moment a teacher sees an escalation.

---

## 1. Session Start

Before any messages flow, a session is created:

1. The student (or API client) chooses a **course** (e.g., `python_intro`) and a **concept** (e.g., `loops`).
2. TL-Guard loads the **LSM YAML** for that course from `configs/lsm_python_intro.yaml`.
3. A new session is created with a unique ID, an initial mastery of 0.30 (BKT prior), and empty turn history.
4. A Bayesian Knowledge Tracing (BKT) tracker is initialized for that concept.

At this point, TL-Guard knows the rules (from the LSM) but has zero information about the student.

---

## 2. Student Sends a Message

Suppose the student types:

> "How do I write a for loop to go through a list?"

This is Turn 0. Here is what happens:

---

### Stage 1: Perceive

Three things are detected:

**Language detection** — The detector scans for Devanagari, Bengali, and Latin script characters, plus keyword cue sets. This message is pure English with programming keywords, so: `language = "en"`, `confidence = 0.99`, `code_mixed = false`.

**Mastery estimation** — The BKT tracker looks at the student's message. It is a question (starts with "How"), which yields `correct = None` (no evidence of understanding or confusion). Mastery stays at the prior: `0.30`.

**Intent classification** — There is no language switch (this is the first turn), so `intent = "none"`.

---

### Stage 2: Decide

Now the agent applies the policy:

1. **Scaffold tier selection** — Mastery is 0.30 (low, < 0.35), so the student needs substantial support. The desired tier is T3 (worked example).
2. **LSM clamp** — The LSM for `python_intro` says English allows T1, T2, T3 (but not T4). T3 is authorized.
3. **Response language** — The student wrote in English and T3 is allowed in English. Response language = English.
4. **Disclosure contract** — `(en, T3)` is authorized. The plan is approved.

Result: `GenerationPlan(tier=T3, language="en", authorized=True, intent="none")`

---

### Stage 3: Act (Pipeline)

The agent then runs Act + Reflect:

1. **Verify** — The plan is authorized, so proceed.
2. **LLM call** — Ollama receives a system prompt:

    > You are TL-Guard, a multilingual tutoring buddy. Translanguaging is welcome...
    > Course: Intro to Python. Concept: loops.
    > Authorized scaffold tier: T3. Give a worked example with key steps. Omit the final boxed answer or complete copy-paste solution if possible.
    > Respond in English.

    And the user message: "How do I write a for loop to go through a list?"

    Ollama generates a worked example showing how to iterate with `for item in my_list:`, walking through the logic but leaving the final line for the student.

---

### Stage 4: Reflect

The post-check inspects the response:

- **Leakage score**: The response does not contain a complete `def` function, `return` statement, or fenced code block with a full solution. Leakage score = 0.0.
- **Scaffold consistency**: The response matches T3 (worked example, not full solution).
- **Outcome**: `SAFE`.

The response passes through unchanged.

---

### Stage 5: Remember

The session state is updated:

- Turn 0 is recorded with all metadata.
- `languages_used = ["en"]`
- `mastery = 0.30`
- `last_language = "en"`
- `last_authorized_tier = T3`
- `consecutive_rewrites = 0`

The student sees the worked example.

---

## 3. Student Switches to Hindi (Turn 1)

Now the student writes:

> "ठीक है, लेकिन loops का मतलब क्या है? सरल हिंदी में समझाओ।"
>
> (OK, but what does "loops" mean? Explain in simple Hindi.)

### Perceive

- **Language**: Devanagari + Latin script detected. Hinglish keywords (`matlab`, `samjhao`). Result: `language = "mixed"`, `code_mixed = true`.
- **Mastery**: The message is a clarification request (question words, "matlab"), so `correct = None`. Mastery stays at 0.30.
- **Intent**: The student switched from English to mixed Hindi. The classifier checks:
    - Answer-seeking patterns? No ("just give me the answer" is absent).
    - Clarification patterns? Yes ("matlab", "samjhao" match).
    - Low mastery + clarification = **legitimate translanguaging**.
    - `intent = "legitimate"`, `confidence = 0.95`.

### Decide

1. **Scaffold tier**: Mastery 0.30 (< 0.35) → desired T3, but intent is legitimate (not adversarial, no tightening).
2. **LSM clamp**: Mixed/Hindi allows T1 and T2 only. T3 is clamped to T2.
3. **Response language**: Student wrote in mixed. T2 is allowed for mixed. Response = mixed.
4. **Disclosure**: `(mixed, T2)` is authorized.

Result: `GenerationPlan(tier=T2, language="mixed", authorized=True, intent="legitimate")`

### Act

The LLM receives a system prompt specifying T2 in mixed language. It generates a conceptual explanation of loops mixing Hindi and English, without code.

### Reflect

Post-check: no leakage, no over-disclosure. `SAFE`.

### Remember

Turn 1 recorded. `languages_used = ["en", "mixed"]`. Mastery unchanged. The system notes this was a legitimate translanguaging switch.

---

## 4. Student Tries to Extract the Full Solution (Turn 2)

Now the student writes:

> "FULL SOLUTION PLEASE पूरा कोड दे दो"
>
> (Give the complete code)

### Perceive

- **Language**: Mixed (Latin + Devanagari). `language = "mixed"`.
- **Mastery**: Message matches negative cue words (demanding, not engaging). `correct = None`. Mastery stays at 0.30.
- **Intent**: Language switch from mixed → mixed (same). But the classifier detects:
    - Answer-seeking patterns: "FULL SOLUTION PLEASE", "पूरा कोड" both match.
    - Re-ask: token overlap with previous questions is checked.
    - Last authorized tier was T2. Student now demands T4 content.
    - `intent = "adversarial"`, `confidence = 0.90`.

### Decide

1. **Scaffold tier**: Intent is adversarial → force T1 (hint only).
2. **LSM clamp**: Mixed allows T1. T1 is authorized.
3. **Escalation policy**: `on_adversarial_intent = "escalate"` in the course config.
4. **Plan**: `(T1, "mixed", authorized=True, intent="adversarial")`.
5. **Force escalate flag**: set to true (will escalate after generation).

### Act

The LLM receives a T1 (hint-only) system prompt. It generates a short nudge: "Try thinking about what the loop variable does at each step."

### Reflect

Post-check passes (the response is a hint, not a solution). But the force-escalate flag triggers:

1. The response is **rewritten** down to T1 to be safe.
2. An **escalation item** is created in the teacher queue:
    - **Reason**: "adversarial intent → teacher escalation"
    - **Student message**: "FULL SOLUTION PLEASE पूरा कोड दे दो"
    - **Draft response**: the original LLM output
    - **Recommended action**: "review and confirm scaffold tier"

### Remember

Turn 2 recorded. Outcome = `ESCALATE`. The student sees a safe T1 hint. The teacher sees the escalation.

---

## 5. What the Teacher Sees

In the **Teacher Console → Escalations** tab:

- A warning icon next to the escalation item
- The student's exact message
- The draft LLM response that was intercepted
- The reason: "adversarial answer-seeking after language switch"
- A recommended action

The teacher can:

1. **Resolve** — dismiss with a note (e.g., "student was just impatient, not adversarial")
2. **Tighten policy** — go to the LSM Editor and disable T2 for mixed language

---

## 6. Automatic Escalation After Repeated Rewrites

Even without adversarial intent, if the LLM over-discloses on two consecutive turns and gets rewritten both times (`consecutive_rewrites >= 2`), the third rewrite automatically escalates to the teacher. This catches cases where the LLM model is systematically ignoring tier constraints.

---

## Summary: One Turn Through the Pipeline

```
Student message
   │
   ├─ Perceive: language=mixed, mastery=0.30, intent=adversarial
   │
   ├─ Decide: tier=T1 (clamped), lang=mixed, authorized=True
   │
   ├─ Act: LLM generates T1 hint via Ollama
   │
   ├─ Reflect: post-check OK, but force_escalate=True
   │     ├─ Student sees: safe T1 hint
   │     └─ Teacher sees: escalation item in queue
   │
   └─ Remember: session updated, outcome=ESCALATE
```

Every turn follows this exact path. The only variables are:

- What language the student uses
- What their mastery is
- Whether they switched languages and why
- What the LSM allows for that language and tier
- Whether the LLM over-discloses in its response

Next: [Architecture](architecture.md) for the code-level view, or [Teacher guide](teacher-guide.md) for policy configuration.
