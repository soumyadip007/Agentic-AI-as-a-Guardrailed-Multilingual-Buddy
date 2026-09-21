# Operationalizing Translanguaging for AI Agents

## Background: García's Translanguaging Framework

Ofelia García, Susana Johnson, and Kate Seltzer (2017) proposed a three-pronged framework for translanguaging pedagogy in human classrooms:

1. **Stance** — The teacher believes that multilingualism is a resource, not a deficit. Students are encouraged to use their full linguistic repertoire.
2. **Design** — The teacher plans instruction to purposefully leverage students' languages. Assignments, materials, and groupings account for multilingual abilities.
3. **Shifts** — During instruction, the teacher makes moment-to-moment adjustments based on what is happening — switching languages, adjusting explanations, responding to student needs in real time.

This framework was designed for human teachers. TL-Guard is the first system to translate these principles into computational constructs for an AI agent.

---

## How TL-Guard Implements Each Principle

### Stance → System Prompt + Language Feature Logging

**Human teacher**: "I welcome all your languages in my classroom."

**TL-Guard implementation**: The system prompt for every LLM call includes:

> "You are TL-Guard, a multilingual tutoring buddy. Translanguaging is welcome: students may mix languages. Never punish or shame language mixing. Stay within the authorized scaffold tier and response language."

Additionally, language-switch events are logged as **features**, not **anomalies**, in the session state. The field `languages_used` records every language the student has used. This stands in contrast to safety-only systems (e.g., NeMo Guardrails) that treat language switches as potential attacks.

**Code**: `src/tl_guard/act/llm_executor.py` → `STANCE_PREAMBLE`

---

### Design → Language–Scaffold Matrix (LSM)

**Human teacher**: "I have planned which parts of today's lesson will be in English and which will leverage students' home languages."

**TL-Guard implementation**: The teacher creates a YAML policy — the **Language–Scaffold Matrix** — that specifies, for each language, which scaffold tiers (T1–T4) are available. This is the computational equivalent of the teacher's lesson plan.

Example: for "Intro to Python", the teacher might decide that Hindi-speaking students can receive hints and explanations in Hindi (T1, T2), but worked examples and solutions should be in English (T3 in English only, T4 nowhere).

This is loaded before each session and enforced on every turn.

**Code**: `configs/lsm_*.yaml`, `src/tl_guard/decide/lsm_engine.py`, `src/tl_guard/config_loader.py`

---

### Shifts → Adaptive Per-Turn Decision Logic

**Human teacher**: "I notice the student is struggling with the concept, so I switch to Bengali to explain, then switch back to English for the code."

**TL-Guard implementation**: Every turn, the Decide module evaluates four things:

1. **Student's language choice** — What language did they use?
2. **Current mastery** — How well do they understand the concept right now? (from BKT)
3. **Scaffold tier** — What level of help should they get?
4. **LSM authorization** — Is this tier allowed in this language?

Based on these, it selects the scaffold tier and response language *for this specific turn*. A student who showed understanding in the last turn gets lighter help (T1). A student who just switched to Hindi for clarification and has low mastery gets T2 in Hindi. A student who demands "full solution" after switching languages gets T1 (tightened) and an escalation.

**Code**: `src/tl_guard/decide/scaffold_selector.py`, `src/tl_guard/decide/language_selector.py`, `src/tl_guard/agent.py`

---

## Summary Table

| García Principle | Human Teacher Behavior | TL-Guard Computational Construct | Module |
|---|---|---|---|
| **Stance** | Welcoming all languages | System prompt + language feature logging | `act/llm_executor.py` |
| **Design** | Planning multilingual instruction | Language–Scaffold Matrix (YAML) | `configs/`, `decide/lsm_engine.py` |
| **Shifts** | Moment-to-moment adjustments | Per-turn mastery + intent + LSM → tier + language | `decide/`, `agent.py` |

This mapping is the first research contribution (C1) of the TL-Guard paper.
