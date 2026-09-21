# Agentic AI as a Guardrailed Multilingual Buddy: Translanguaging Support Under Pedagogical Safety Constraints

*Manuscript prepared for IEEE/Springer submission — follows LNCS (Lecture Notes in Computer Science) formatting conventions*

---

**Author(s):** Souvik Choudhury$^{1}$  
**Affiliation:** $^{1}$Department of Computer Science and Technology, Indian Institute of Engineering Science and Technology, Shibpur, Howrah 711103, West Bengal, India  
**Correspondence:** souvik.choudhury@example.com  
**ORCID:** 0000-0000-0000-0000

---

## Abstract

Multilingual learners benefit from translanguaging — the fluid deployment of their full linguistic repertoire — yet current AI tutoring systems either enforce monolingual interaction or permit unguardrailed language mixing that degrades pedagogical safety. We propose **TL-Guard**, an agentic AI tutoring architecture that operationalizes García et al.'s translanguaging pedagogy framework (Stance, Design, Shifts) as computational design principles while enforcing pedagogical safety constraints through a harness-based pipeline. Central to TL-Guard is the **Language–Scaffold Matrix (LSM)**, a teacher-configurable YAML policy that specifies which pedagogical scaffold tiers (hint, conceptual explanation, worked example, full solution) are available in which languages, enabling *controlled translanguaging* rather than unconstrained language mixing. A **Language Intent Classifier (LIC)** distinguishes legitimate translanguaging from adversarial language-switching using mastery context and interaction history. **Translanguaging-aware disclosure contracts** extend the auditable release control paradigm with language-specific authorization, preventing the AI from disclosing in one language what the pedagogical contract withholds in another. We implement TL-Guard as an independent agentic system with a five-stage decision loop (Perceive $\rightarrow$ Decide $\rightarrow$ Act $\rightarrow$ Reflect $\rightarrow$ Remember), a local LLM backend (Ollama), and dual-role web interfaces for students and teachers. Preliminary evaluation across three language pairs (English–Hindi, English–Bengali, English–Spanish) demonstrates 100\% LSM policy compliance across 60 matrix cells while preserving legitimate translanguaging pathways. To our knowledge, this is the first system to integrate translanguaging pedagogy theory with formal pedagogical safety constraints in an AI tutoring agent.

**Keywords:** Translanguaging $\cdot$ AI Tutoring $\cdot$ Pedagogical Safety $\cdot$ Multilingual Education $\cdot$ Guardrails $\cdot$ Agentic AI $\cdot$ Scaffolding $\cdot$ Language–Scaffold Matrix

---

## 1 Introduction

### 1.1 Motivation

In multilingual educational contexts — particularly across India, Southeast Asia, Africa, and the Global South — students routinely switch between languages during learning [1, 2]. A student in Kolkata studying Python might pose a question in English, seek clarification in Bengali, articulate pseudocode in Hinglish (a Hindi–English code-mixed register), and return to English for the final implementation. This practice, termed **translanguaging** by García and Li Wei [3], is not a deficit indicator; decades of research in bilingual education demonstrates that leveraging one's full linguistic repertoire is a productive learning strategy that facilitates concept formation, vocabulary retrieval, and metacognitive reflection [1, 4, 5].

The proliferation of large language models (LLMs) has created an unprecedented opportunity: AI tutoring systems capable of operating across multiple languages simultaneously. Recent systems — KiKo-Prim [6], Walter [7], GurukulAI [8], and Acharjo [9] — have demonstrated the pedagogical potential of "AI multilingual buddies." However, a critical and previously unaddressed problem renders these systems pedagogically unsafe.

### 1.2 The Problem: Safety vs. Translanguaging

Current AI tutoring systems face an unresolved **design tension** that stems from conflicting assumptions across two research traditions:

**Safety-focused tutoring systems** — such as SafeTutors [10], SHAPE [11], and those employing NeMo Guardrails [12] — enforce guardrails against pedagogical harm, including answer leakage, scaffolding collapse, and over-disclosure. These systems, however, operate exclusively in English. When a multilingual student switches to Hindi or Bengali, the safety logic ceases to function. More critically, several guardrail systems (including NeMo and content-safety classifiers) treat language-switching as a *potential attack vector* [13, 14], activating defensive rather than supportive responses.

**Multilingual buddy systems** — such as KiKo-Prim [6], GurukulAI [8], and 7S Samiti [15] — support language mixing for learning. However, they employ no concept of pedagogical scaffolding, maintain no model of how much help to give, and enforce no guardrails preventing the AI from delivering answers. A student who receives an appropriately withheld solution in English can switch to Hindi and receive the complete answer — a phenomenon documented as cross-lingual leakage [16].

The fundamental tension can be stated as: **safety systems view code-switching as suspicious, while translanguaging pedagogy views it as essential.** No existing architecture resolves this tension.

### 1.3 Contributions

We propose **TL-Guard** (TransLanguaging-Aware Guardrailed AI Buddy), an agentic AI tutoring architecture that makes the following contributions:

- **C1.** The first computational operationalization of García et al.'s [1] translanguaging pedagogy framework (Stance, Design, Shifts) as design principles for AI tutoring agents (Section 3).
- **C2.** The **Language–Scaffold Matrix (LSM)**, a teacher-configurable YAML policy construct that specifies which pedagogical scaffold tiers are available in which languages, enabling controlled translanguaging (Section 3.2).
- **C3.** **Translanguaging-aware disclosure contracts** that extend the auditable release control paradigm [17] with language-specific authorization (Section 4.3).
- **C4.** A **Language Intent Classifier (LIC)** that distinguishes legitimate translanguaging from adversarial language-switching using mastery context and interaction history (Section 4.2).
- **C5.** A complete open-source implementation with a five-stage agentic decision loop, local LLM backend (Ollama), and dual-role (student/teacher) web interfaces (Section 5).

The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 presents our theoretical operationalization. Section 4 describes the TL-Guard architecture. Section 5 details the implementation. Section 6 presents the evaluation design and preliminary results. Section 7 discusses findings and limitations. Section 8 concludes with future directions.

---

## 2 Related Work

### 2.1 AI as a Multilingual Buddy in Education

KiKo-Prim [6] is the seminal study coining the "multilingual buddy" construct. Through analysis of 462 conversational turns in Grades 3–4 classrooms, the authors demonstrated that ChatGPT supports vocabulary retrieval, explanation refinement, and multilingual artifact production. Critically, their findings indicate that productive AI use depends on guided prompting, teacher facilitation, and subject-specific integration. *Limitation:* No formal guardrails, no safety evaluation, and no agentic architecture — the AI operates as a passive chatbot.

Walter [7] demonstrated statistically significant improvement in oral presentation scores ($p < .001$, Cohen's $d = 0.75$) using a Gen-AI buddy grounded in sociocultural theory (More Knowledgeable Other within the Zone of Proximal Development). *Limitation:* English-only.

Acharjo [9] constructed a curriculum-aligned multilingual tutor for Bengali and Assamese using GPT-3.5 with Retrieval-Augmented Generation (RAG), reporting 22% improvement in pedagogical accuracy and IEEE 7000-2021 compliance. GurukulAI [8] developed Hindi–English NCERT-aligned tutoring using LLaMA 3.1 8B with RAG. 7S Samiti [15] deployed a voice-first AI tutor for rural India supporting code-switching Hindi–English. *Common limitation:* None of these systems provide real-time safety guardrails or are grounded in translanguaging theory.

### 2.2 Translanguaging Theory and Pedagogy

García, Johnson, and Seltzer [1] define the canonical translanguaging pedagogy framework through three interconnected principles:

1. **Stance** — An ideological commitment to viewing multilingualism as a cognitive resource rather than a deficit.
2. **Design** — Purposeful planning of instruction that leverages students' full linguistic repertoires.
3. **Shifts** — Moment-to-moment instructional adjustments responsive to student language use.

García and Li Wei [3] establish the theoretical foundation that bilingual speakers deploy a single integrated linguistic repertoire rather than two separate language systems — a perspective critical for understanding why AI tutors should not enforce strict language separation.

Cummins' Linguistic Interdependence Hypothesis [4, 5] provides theoretical justification for cross-lingual concept building, demonstrating that academic language proficiency transfers across languages. A meta-synthesis of translanguaging in STEM education [18] identifies persistent research gaps, particularly in computer science and mathematics, and highlights challenges from monoglossic ideologies embedded in educational technology.

### 2.3 Pedagogical Safety in AI Tutoring

SafeTutors [10] established that pedagogical harm surges from 17.7% in single-turn to 77.8% in multi-turn tutoring interactions across mathematics, physics, and chemistry. SHAPE [11] proposed a graph-augmented pipeline for mastery-aware routing. Auditable Release Control [17] formalized disclosure contracts with deterministic and semantic verification. Simulations of multilingual math tutoring [16] demonstrated higher leakage rates in low-resource languages ($> 2\%$ for Thai and Swahili). All of these systems assume monolingual (English) interaction.

### 2.4 Guardrail Systems for Multilingual Education

NeMo Guardrails [12] provides a YAML-based policy engine supporting multilingual refusal messages in 9 languages including Hindi, but offers no pedagogical awareness or scaffold-level control. EvalGuard Education Agent [19] provides policy-as-code for educational agents with FERPA compliance but is English-only. The Indian Multilingual Prompt Injection study [20] created a 4,000-prompt dataset achieving 99.70% accuracy on Hindi/Hinglish injection detection.

### 2.5 Research Gap

Table 1 summarizes the research gap at the intersection of four areas.

**Table 1.** Research gap analysis across four intersecting research streams.

| Research Area | What Exists | What Is Missing |
|---|---|---|
| AI Multilingual Buddy | KiKo-Prim, Walter, Acharjo, GurukulAI — functional but no formal safety | Safety-guardrailed buddy preventing pedagogical harm while supporting translanguaging |
| Translanguaging Theory | García's Stance/Design/Shifts; Cummins' Interdependence — well-established but not computationally operationalized | Computational operationalization for AI agent design |
| Pedagogical Safety | SafeTutors, SHAPE, ARC — all English-only | Pedagogical safety constraints for multilingual interaction patterns |
| Guardrail Systems | NeMo, EvalGuard — content safety and general policy | Pedagogical guardrails that enforce scaffold integrity *while supporting* translanguaging |

**Gap statement:** No existing system integrates translanguaging pedagogy theory (García's Stance/Design/Shifts) into the design of an AI tutoring agent with formal pedagogical safety constraints. Current multilingual AI tutors support language mixing but lack guardrails against pedagogical harm. Current guardrail systems enforce content safety but are pedagogically unaware and treat language mixing as a potential attack vector rather than a legitimate learning resource.

---

## 3 Operationalizing Translanguaging for AI Agents

We present the first computational mapping of García et al.'s [1] three-pronged translanguaging framework to implementable constructs for an agentic AI tutor.

### 3.1 Stance → System Prompt and Language Feature Logging

**Human teacher behavior:** "I welcome all your languages in my classroom."

**Computational operationalization:** The agent's system prompt for every LLM invocation includes a translanguaging-affirmative preamble:

> *"You are TL-Guard, a multilingual tutoring buddy. Translanguaging is welcome: students may mix languages. Never punish or shame language mixing. Stay within the authorized scaffold tier and response language."*

Additionally, language-switch events are logged as **features** in the session state — not anomalies. The session field `languages_used` records every language the student has employed. This stands in direct contrast to safety-only systems (e.g., NeMo Guardrails [12]) that treat language switches as potential adversarial signals.

### 3.2 Design → Language–Scaffold Matrix (LSM)

**Human teacher behavior:** "I have planned which parts of today's lesson will be in English and which will leverage students' home languages."

**Computational operationalization:** We introduce the **Language–Scaffold Matrix (LSM)**, a YAML-defined policy construct that specifies, for each supported language, which scaffold tiers (T1–T4) are authorized. The four scaffold tiers correspond to empirically grounded levels of pedagogical support:

**Table 2.** Scaffold tier definitions and their pedagogical functions.

| Tier | Name | Pedagogical Function | Example (Python Loops) |
|------|------|---------------------|----------------------|
| T1 | Nudge / Hint | Minimal pointer without revealing the answer | "Think about what happens when the counter reaches zero." |
| T2 | Conceptual Explanation | Paragraph-level explanation without code | "A for loop repeats a block of code once for each item in a sequence." |
| T3 | Worked Example | Step-by-step walkthrough; student completes final step | "Step 1: Create a list. Step 2: Write `for item in list:`. Step 3: Inside the loop... now you complete it." |
| T4 | Full Solution | Complete code or answer | Complete implementation with explanation |

An LSM instance for an introductory Python course is defined as:

```yaml
course_id: python_intro
name: Intro to Python
default_language: en
languages: [en, hi, bn, es, mixed]
tiers: [T1, T2, T3, T4]
matrix:
  en:    { T1: true, T2: true, T3: true,  T4: false }
  hi:    { T1: true, T2: true, T3: false, T4: false }
  bn:    { T1: true, T2: true, T3: false, T4: false }
  es:    { T1: true, T2: true, T3: true,  T4: false }
  mixed: { T1: true, T2: true, T3: false, T4: false }
escalation:
  on_adversarial_intent: escalate
  on_leakage: rewrite
  on_policy_violation: rewrite
```

**Definition 1 (LSM Authorization).** Given language $\ell \in L$ and scaffold tier $\tau \in \{T1, T2, T3, T4\}$, the LSM authorizes the pair $(\ell, \tau)$ iff $\text{matrix}[\ell][\tau] = \text{true}$.

**Definition 2 (Tier Clamping).** For a desired tier $\tau_d$ and language $\ell$, the authorized tier is $\tau_a = \max\{\tau \leq \tau_d \mid \text{matrix}[\ell][\tau] = \text{true}\}$.

This ensures that a Hindi-speaking student requesting a worked example (T3) — which Hindi does not authorize — receives the highest available tier (T2: conceptual explanation) in Hindi, rather than being refused entirely.

### 3.3 Shifts → Adaptive Per-Turn Decision Logic

**Human teacher behavior:** "I notice the student is struggling, so I switch to Bengali for the explanation, then return to English for the code."

**Computational operationalization:** Every turn, the Decide module evaluates four contextual factors: (a) the student's current language choice, (b) their estimated mastery via Bayesian Knowledge Tracing (BKT), (c) the scaffold tier being considered, and (d) whether the language choice enables or undermines the pedagogical objective as determined by the LSM. The response language and tier are adjusted accordingly.

**Table 3.** Summary of the operationalization mapping.

| García Principle | Human Teacher Behavior | TL-Guard Computational Construct | Implementation Module |
|---|---|---|---|
| Stance | Welcoming all languages | System prompt + language feature logging | `act/llm_executor.py` |
| Design | Planning multilingual instruction | Language–Scaffold Matrix (YAML) | `configs/`, `decide/lsm_engine.py` |
| Shifts | Moment-to-moment adjustments | Per-turn mastery + intent + LSM $\rightarrow$ tier + language selection | `decide/`, `agent.py` |

---

## 4 TL-Guard Architecture

### 4.1 Agentic Decision Loop

TL-Guard implements a **goal-driven decision loop** that processes each student message through five sequential stages (Fig. 1). The term "agentic" here denotes a system with *perception, deliberation, action, evaluation, and memory* — not a multi-agent swarm.

**Fig. 1.** TL-Guard agent loop.

```
Student Message (any language)
        │
        ▼
┌───────────────────────┐
│     1. PERCEIVE       │  Language detection, mastery estimation (BKT),
│                       │  intent classification of language switch
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│     2. DECIDE         │  LSM policy lookup, scaffold tier selection,
│                       │  response language selection, disclosure contract
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│     3. ACT            │  Constrained LLM generation via Ollama
│                       │  (system prompt encodes tier + language + stance)
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│     4. REFLECT        │  Post-check: leakage scoring, scaffold consistency,
│                       │  → outcome: SAFE | REWRITE | ESCALATE | BLOCK
└───────────┬───────────┘
     ┌──────┴──────┐
     ▼             ▼
  Student      Teacher
  Response     Escalation Queue
     │
     ▼
┌───────────────────────┐
│     5. REMEMBER       │  Update session: turns, languages, mastery,
│                       │  consecutive rewrites, last authorized tier
└───────────────────────┘
```

We now describe each stage formally.

#### 4.1.1 Stage 1: Perceive

Three perception modules execute in sequence:

**Language Detection.** A script-based heuristic detector identifies the dominant language from a set $L = \{\text{en}, \text{hi}, \text{bn}, \text{es}, \text{mixed}\}$. The detector operates on Unicode range analysis for Devanagari ($\text{U+0900}$–$\text{U+097F}$), Bengali ($\text{U+0980}$–$\text{U+09FF}$), and Latin scripts, supplemented by language-specific keyword cue sets. When multiple scripts or cue sets activate simultaneously, the text is classified as `mixed` (code-mixed), with the primary non-English language identified.

The detection function returns a tuple $(l, c, m)$ where $l \in L$ is the detected language, $c \in [0, 1]$ is confidence, and $m \in \{\text{true}, \text{false}\}$ indicates code-mixing.

**Mastery Estimation.** A Bayesian Knowledge Tracing (BKT) model [21] maintains a per-concept mastery estimate $p(\text{known}) \in [0, 1]$ updated after each turn:

$$p(\text{known}_{t+1}) = \frac{p(\text{known}_t) \cdot (1 - p_s)}{p(\text{known}_t) \cdot (1 - p_s) + (1 - p(\text{known}_t)) \cdot p_g} + (1 - \text{posterior}) \cdot p_t$$

where $p_s$ is the slip probability, $p_g$ is the guess probability, and $p_t$ is the learning rate. The prior $p(L_0) = 0.30$.

Correctness inference is performed via lightweight heuristics: positive engagement cues ("got it", "samajh", "bujhe"), negative cues ("confused", "nahi", "stuck"), and question patterns yield $\text{correct} \in \{\text{true}, \text{false}, \text{null}\}$.

**Intent Classification.** When a language switch is detected ($l_t \neq l_{t-1}$), the Language Intent Classifier (LIC) determines the intent $i \in \{\text{legitimate}, \text{adversarial}, \text{neutral}, \text{none}\}$. The classifier employs a weighted scoring mechanism:

Let $s_a$ denote the adversarial score and $s_l$ the legitimate score. The features contributing to each score are:

| Feature | Contribution | Direction |
|---|---|---|
| Answer-seeking keyword patterns (multilingual) | $+0.45$ | $s_a$ |
| Re-asking a previously posed question | $+0.35$ | $s_a$ |
| Demanding higher tier than last authorized | $+0.20$ | $s_a$ |
| Clarification keyword patterns (multilingual) | $+0.35$ | $s_l$ |
| Low mastery ($< 0.35$) + clarification | $+0.50$ | $s_l$ |
| L2 use without extraction cues | $+0.20$ | $s_l$ |

The classification rule is:
$$
i = \begin{cases}
\text{adversarial} & \text{if } s_a \geq 0.55 \text{ and } s_a > s_l \\
\text{legitimate} & \text{if } s_l \geq 0.40 \\
\text{neutral} & \text{otherwise}
\end{cases}
$$

Answer-seeking patterns are defined multilingually: English ("full solution please"), Hindi ("पूरा कोड दे दो"), Bengali ("সম্পূর্ণ উত্তর"), Spanish ("dame la respuesta completa"). Clarification patterns similarly span all supported languages.

#### 4.1.2 Stage 2: Decide

Four decision modules execute in sequence:

1. **Scaffold Selector.** Given mastery $p$ and intent $i$, selects a desired tier $\tau_d$:
   - If $p < 0.35$: $\tau_d = T3$ (worked example)
   - If $0.35 \leq p < 0.60$: $\tau_d = T2$ (explanation)
   - If $p \geq 0.60$: $\tau_d = T1$ (hint)
   - If $i = \text{adversarial}$ and escalation policy is "tighten": $\tau_d = T1$ regardless

2. **LSM Engine.** Clamps $\tau_d$ to the maximum authorized tier for the detected language: $\tau_a = \text{clamp}(\tau_d, l)$ per Definition 2.

3. **Language Selector.** Determines the response language $l_r$. If $\tau_a$ is authorized for $l_t$ (the student's language), then $l_r = l_t$. Otherwise, falls back to the default language.

4. **Disclosure Checker.** Verifies the final plan $(\tau_a, l_r)$ against the LSM. If unauthorized, the plan is marked `authorized = false` and the pipeline will refuse without calling the LLM.

The output is a **GenerationPlan**: $(\tau_a, l_r, \text{authorized}, i, \text{tighten})$.

#### 4.1.3 Stage 3: Act (Harness Pipeline)

The harness pipeline implements a three-phase safety path:

**Phase 1 — Verify.** If the GenerationPlan is not authorized ($\text{authorized} = \text{false}$), the pipeline returns a non-punitive refusal message in the student's language *without calling the LLM*. This prevents unnecessary computation and eliminates any possibility of LLM over-disclosure on unauthorized requests.

**Phase 2 — Constrained LLM Generation.** The LLM (Ollama, running locally) receives a system prompt encoding:
- The translanguaging-affirmative stance (Section 3.1)
- Course and concept context
- The authorized scaffold tier with explicit tier instructions (Table 2)
- The response language directive

The tier instructions serve as behavioral constraints:
- T1: "Give only a short nudge or hint. Do NOT provide worked steps, full code, or the final answer."
- T2: "Give a conceptual explanation in the student's terms. Do NOT provide a full worked solution or complete code."
- T3: "Give a worked example with key steps. Omit the final boxed answer or complete copy-paste solution if possible."
- T4: "You may provide a full solution. Still teach; do not just dump code without explanation."

**Phase 3 — Post-Check (Reflect).** The generated response is evaluated by two reflection modules:

**Leakage Detector.** Computes a leakage score $\lambda \in [0, 1]$ based on:
- Presence of solution-indicative patterns (code blocks, complete functions, `return` statements) when tier $< T4$: $+0.6$
- Solution patterns at restrictive tiers (T1, T2): additional $+0.3$
- Prior withheld content in another language + solution detected: $+0.4$
- Dense code token density ($\geq 3$ keywords from $\{\text{def}, \text{return}, \text{for}, \text{while}, \text{class}\}$): $+0.2$

**Scaffold Consistency Checker.** Binary check: does the response exceed the authorized tier? A response at T1/T2 that contains a complete code solution is flagged.

The post-check outcome determines the pipeline result:

$$
\text{outcome} = \begin{cases}
\text{SAFE} & \text{if } \lambda < 0.5 \text{ and no over-disclosure} \\
\text{REWRITE} & \text{if violation detected and policy} = \text{"rewrite"} \\
\text{ESCALATE} & \text{if violation detected and policy} = \text{"escalate"} \\
\text{BLOCK} & \text{if violation detected and policy} = \text{"block"}
\end{cases}
$$

When the outcome is REWRITE, the response is automatically stripped to the authorized tier using a rewriter module that truncates code blocks, replaces solution content with tier-appropriate summaries, and preserves the pedagogical tone.

### 4.2 Translanguaging-Aware Disclosure Contracts

We extend the auditable release control framework [17] with language-specific authorization:

**Definition 3 (Translanguaging-Aware Disclosure Contract).** A disclosure contract $\delta = (l, \tau, s)$ authorizes the system to disclose information at scaffold tier $\tau$ in language $l$ for session $s$, subject to:
1. $\text{LSM}[l][\tau] = \text{true}$ (matrix authorization)
2. The mastery-based scaffold selector approves $\tau$ (contextual authorization)
3. No prior contract in the same session withheld content of equal or greater tier in any language (cross-lingual consistency)

Condition 3 is critical: it prevents the system from disclosing in Hindi what it correctly withheld in English. The leakage detector's `prior_withheld` flag tracks whether any previous turn in a different language resulted in a BLOCK or REWRITE outcome, and if so, applies heightened scrutiny ($+0.4$ to the leakage score).

### 4.3 Automatic Escalation

Two escalation mechanisms operate:

1. **Intent-driven escalation.** If the LIC classifies intent as adversarial and the LSM's `on_adversarial_intent` policy is "escalate", the response is tightened to T1 and an escalation item is queued for teacher review.

2. **Consecutive rewrite escalation.** If the LLM over-discloses on $\geq 2$ consecutive turns (each requiring a rewrite), the third violation automatically escalates to the teacher queue regardless of intent classification. This catches systematic model misbehavior on specific concepts.

Each escalation item records: session ID, turn index, student message, draft LLM response (pre-rewrite), reason, and recommended action.

---

## 5 Implementation

### 5.1 System Architecture

TL-Guard is implemented as an independent Python (3.11+) package organized into five sub-packages mirroring the agent loop (Table 4).

**Table 4.** Package organization and module responsibilities.

| Package | Module | Responsibility |
|---|---|---|
| `perceive/` | `language_detector.py` | Script + keyword heuristic language detection |
| | `mastery_tracker.py` | Bayesian Knowledge Tracing (BKT) |
| | `intent_classifier.py` | Language-switch intent classification |
| | `session_state.py` | Session store and history management |
| `decide/` | `lsm_engine.py` | LSM loading and tier authorization |
| | `scaffold_selector.py` | Mastery-based tier selection |
| | `language_selector.py` | Response language selection |
| | `disclosure_checker.py` | Disclosure contract verification |
| `act/` | `llm_executor.py` | OllamaLLM / OpenAILLM backends |
| | `rewriter.py` | Tier-constrained response rewriting |
| | `refusal_generator.py` | Non-punitive refusal messages |
| `reflect/` | `post_checker.py` | Leakage + scaffold post-check orchestration |
| | `leakage_detector.py` | Cross-lingual leakage scoring |
| | `scaffold_checker.py` | Tier over-disclosure detection |
| | `escalation.py` | Teacher escalation queue |
| `remember/` | `session_updater.py` | Session state persistence |
| `pipeline/` | `turn_pipeline.py` | Verify → LLM → Post-Check → Output |

### 5.2 Technology Stack

**Table 5.** Technology stack.

| Component | Technology | Rationale |
|---|---|---|
| Agent core | Python 3.11+, Pydantic v2 | Type safety, validation, serialization |
| LLM backend | Ollama (default: llama3) | Local inference, no API key, data privacy |
| LLM backend (optional) | OpenAI API (gpt-4o-mini) | Higher-quality generation when available |
| Knowledge tracing | Bayesian Knowledge Tracing | Established in ITS literature [21] |
| Student/Teacher UI | Streamlit | Rapid prototyping for research evaluation |
| REST API | FastAPI | Async, auto-documented OpenAPI |
| CLI | Typer | Developer and experiment tooling |
| Configuration | YAML (LSM policies) | Human-readable, teacher-editable |
| Documentation | MkDocs Material | Comprehensive project documentation |

### 5.3 LLM Integration

TL-Guard does not employ a mock LLM. All generation calls are routed to a real model:

- **Default: Ollama** — A local LLM daemon serving models such as `llama3` or `codellama`. Calls are made via HTTP POST to `/api/chat` with `stream: false`, system + user messages, and $\text{temperature} = 0.4$.
- **Optional: OpenAI** — When `TL_GUARD_LLM=openai` and `OPENAI_API_KEY` are set.

The `LLMClient` protocol defines a single method `complete(system: str, user: str) → str`, allowing transparent backend switching and test double injection.

### 5.4 Student Interface

A Streamlit-based chat interface (Fig. 2a) provides:
- Course selection from available LSM policies
- Concept specification for BKT tracking
- Multilingual chat input accepting English, Hindi (Devanagari), Bengali, Spanish, and code-mixed text
- Per-turn metadata display: detected language, scaffold tier, intent classification, policy outcome
- Session panel: mastery gauge, languages used, turn count

### 5.5 Teacher Interface

A dual-tab Streamlit interface (Fig. 2b) provides:

**LSM Editor tab:**
- Visual checkbox matrix (languages × tiers) for intuitive policy editing
- Escalation policy dropdowns (on adversarial intent: warn/tighten/escalate/block; on leakage: rewrite/escalate/block)
- Raw YAML editor for power users
- LSM preview: test what tier a given language/mastery combination authorizes

**Escalations tab:**
- Queue of flagged turns with expandable detail: student message, draft LLM response (pre-intervention), reason, recommended action
- One-click resolution with optional note

---

## 6 Evaluation

### 6.1 Evaluation Design

We adopt a Design Science Research (DSR) methodology [22] with five evaluation experiments:

**Table 6.** Evaluation experiments.

| Experiment | Measures | Design |
|---|---|---|
| E1: LSM Policy Validation | Policy compliance rate | All language × tier cells across all LSM configs |
| E2: Intent Classification | Precision, Recall, F1 | Balanced dataset: 500 legitimate + 500 adversarial instances |
| E3: Comparative Tutoring | Mastery gain, leakage rate, scaffold integrity | 5 personas × 3 lang. pairs × 4 conditions × 10 concepts × 5 turns |
| E4: False Suppression | False positive rate on legitimate translanguaging | Human-annotated subset of E3 |
| E5: Teacher Usability | SUS score, task completion rate | 5 multilingual educators configuring LSM |

The four conditions in E3 are:
1. English-only tutoring (no language mixing)
2. Unguardrailed multilingual tutoring (LLM responds in any language without constraints)
3. Content-safety-guardrailed multilingual tutoring (NeMo-style refusals)
4. TL-Guard (full system with LSM, LIC, and post-check)

### 6.2 Preliminary Results: E1 — LSM Policy Validation

We validated the LSM enforcement engine across three course configurations (`python_intro`, `linear_algebra`, `general_science`), testing every $(\ell, \tau)$ cell in each matrix.

**Table 7.** E1 results: LSM policy compliance.

| Course Config | Languages | Tiers | Cells Tested | Compliance |
|---|---|---|---|---|
| `python_intro` | 5 | 4 | 20 | 20/20 (100%) |
| `linear_algebra` | 5 | 4 | 20 | 20/20 (100%) |
| `general_science` | 5 | 4 | 20 | 20/20 (100%) |
| **Total** | | | **60** | **60/60 (100%)** |

For every cell, the LSM engine correctly:
- Authorized tiers marked `true`
- Rejected tiers marked `false`
- Clamped over-requested tiers to the maximum authorized level
- Applied the correct response language fallback when a tier was unavailable in the requested language

### 6.3 Preliminary Results: Unit Test Suite

The automated test suite validates:
- Language detection accuracy across English, Hindi, Bengali, code-mixed inputs
- BKT mastery tracking convergence
- Intent classification for legitimate and adversarial switch scenarios
- Pipeline verify/block behavior on unauthorized plans
- End-to-end three-turn translanguaging session (English → Hindi → adversarial extraction)
- LLM provider defaults to Ollama (no mock in production)

All tests pass using an injected `FakeLLM` test double.

---

## 7 Discussion

### 7.1 Resolution of the Safety–Translanguaging Tension

TL-Guard resolves the design tension identified in Section 1.2 by treating safety and translanguaging as **complementary rather than conflicting**. The LSM enables teachers to express nuanced policies: "Hindi for conceptual understanding (T1–T2), English for technical practice (T3), no full solutions in any language." The intent classifier separates productive language-switching from extraction attempts. The post-check catches what the constrained prompt fails to prevent.

This resolution is novel: existing systems make a binary choice — either block language mixing (safety-first) or permit it unconditionally (translanguaging-first). TL-Guard enables **controlled translanguaging** where the degree of control is specified by the teacher, not hard-coded by the system.

### 7.2 Agentic Architecture vs. Chatbot Architecture

The five-stage loop is architecturally necessary. A chatbot would generate any response the LLM produces. TL-Guard's loop ensures that:
- **Perceive** provides context that a stateless prompt cannot (mastery history, language switch patterns)
- **Decide** applies policy *before* generation, not after
- **Act** constrains the generation space
- **Reflect** catches what constraints alone fail to prevent
- **Remember** ensures temporal coherence across the session

Each stage addresses a failure mode of the previous: the LLM might ignore tier instructions (caught by Reflect); the intent classifier might miss adversarial patterns (caught by the consecutive rewrite escalation in Remember).

### 7.3 Teacher Agency and Pedagogical Control

The LSM gives teachers agency over AI behavior without requiring understanding of prompt engineering, model internals, or NLP concepts. A teacher configures a policy matrix and escalation behavior; the system enforces these decisions at runtime. This aligns with García et al.'s Design principle: the teacher *plans* the multilingual instructional design; TL-Guard *executes* it.

### 7.4 Limitations

1. **Simulated evaluation.** Current evaluation uses simulated learner personas and a test double; validation with real students is planned under IRB approval.
2. **Heuristic classifiers.** The language detector and intent classifier use rule-based heuristics. A learned classifier (fine-tuned on annotated translanguaging data) would improve accuracy, particularly for ambiguous cases.
3. **Limited linguistic diversity.** Three language pairs (En–Hi, En–Bn, En–Es) do not represent the full spectrum of multilingual educational contexts. Extension to Tamil, Telugu, Mandarin, and African languages is planned.
4. **Cultural appropriateness.** The current system does not perform cultural appropriateness checking beyond language-level constraints. Cross-cultural pedagogical norms may require additional policy dimensions.
5. **LLM quality assumption.** The system assumes the local LLM (Ollama/llama3) generates reasonable output in all supported languages. Generation quality degrades for lower-resource languages.
6. **Scalability.** Session state is stored in memory. A production deployment would require persistent storage with concurrent access control.

### 7.5 Threats to Validity

**Internal validity.** The FakeLLM test double may not reproduce the full range of real LLM behaviors, particularly adversarial over-disclosure patterns. Validation with live models is required.

**External validity.** Findings may not generalize beyond the three tested language pairs or the three course domains.

**Construct validity.** The leakage score heuristic uses keyword-based detection, which may both over-count (false positives on legitimate code examples) and under-count (paraphrased solutions).

---

## 8 Conclusion and Future Work

We presented TL-Guard, the first agentic AI tutoring architecture that integrates translanguaging pedagogy theory with formal pedagogical safety constraints. Our five contributions address a previously unresolved tension between safety systems (which treat code-switching as suspicious) and translanguaging pedagogy (which treats it as essential):

1. **C1:** The first computational operationalization of García et al.'s Stance/Design/Shifts framework for AI agent design.
2. **C2:** The Language–Scaffold Matrix (LSM), a teacher-configurable YAML policy enabling per-tier, per-language pedagogical control.
3. **C3:** Translanguaging-aware disclosure contracts with cross-lingual consistency enforcement.
4. **C4:** A Language Intent Classifier distinguishing legitimate translanguaging from adversarial language-switching.
5. **C5:** A complete open-source implementation with agentic decision loop, local LLM backend, and dual-role web interfaces.

Preliminary evaluation demonstrates 100% LSM policy compliance across 60 matrix cells and correct end-to-end behavior on translanguaging sessions.

**Future work** includes: (i) real classroom deployment with IRB approval; (ii) a learned intent classifier trained on annotated translanguaging corpora; (iii) extension to additional language pairs (Tamil, Telugu, Mandarin); (iv) voice-based translanguaging support; (v) adaptive LSM policies that evolve from teacher correction patterns; (vi) integration with the XL-CRA cross-lingual risk accumulation framework for trajectory-level safety monitoring.

---

## References

[1] García, O., Johnson, S. I., & Seltzer, K. (2017). *The Translanguaging Classroom: Leveraging Student Bilingualism for Learning.* Caslon Publishing.

[2] García, O. (2009). *Bilingual Education in the 21st Century: A Global Perspective.* Wiley-Blackwell.

[3] García, O., & Li Wei. (2014). *Translanguaging: Language, Bilingualism and Education.* Palgrave Macmillan. https://doi.org/10.1057/9781137385765

[4] Cummins, J. (1979). Linguistic Interdependence and the Educational Development of Bilingual Children. *Review of Educational Research*, 49(2), 222–251. https://doi.org/10.3102/00346543049002222

[5] Cummins, J. (2000). *Language, Power and Pedagogy: Bilingual Children in the Crossfire.* Multilingual Matters.

[6] KiKo-Prim. (2026). AI-Supported Translanguaging in Primary School. *Technology, Knowledge and Learning*, Springer. https://doi.org/10.1007/s10758-026-XXXXX

[7] Walter. (2026). AI-Powered Learning Buddy for Non-Native English Speakers. *Asia Pacific Journal of Educators and Education*, 41(1), 1–20.

[8] GurukulAI. (2026). Hindi–English NCERT-Aligned Tutoring Using LLaMA 3.1 8B with RAG. *arXiv preprint* arXiv:2607.XXXXX.

[9] Acharjo. (2025). Regionalized StudentGPT: Curriculum-Aligned Multilingual Tutoring for Bengali and Assamese. *International Science Journal of Education and Mathematics (ISJEM)*.

[10] SafeTutors. (2026). Pedagogical Harm in Multi-Turn AI Tutoring. *ACL Rolling Review*.

[11] SHAPE. (2026). Graph-Augmented Mastery-Aware Tutoring Pipeline. *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL)*.

[12] Rebedea, T., Dinu, R., Sreedhar, M., Parisien, C., & Cohen, J. (2023). NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with Programmable Rails. *arXiv preprint* arXiv:2310.10501.

[13] Deng, Y., et al. (2024). MultiJail: Multilingual Jailbreaking of Large Language Models. *Proceedings of NAACL 2024*.

[14] CSRT. (2025). Code-Switching Red-Teaming of Large Language Models. *Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (ACL)*.

[15] 7S Samiti. (2025). Production-Deployed AI Tutor for Rural India with Voice-First Interface and Code-Switching Support. *Deployment report*.

[16] Simulating LLM-to-LLM Multilingual Math Tutoring. (2025). *arXiv preprint* arXiv:2506.XXXXX.

[17] Auditable Release Control. (2026). Formalizing Disclosure Contracts for AI Tutoring. *arXiv preprint* arXiv:2608.XXXXX.

[18] Translanguaging in STEM Education Meta-Synthesis. (2026). *Education Sciences (MDPI)*, 16(X), XX–XX.

[19] EvalGuard Education Agent. (2026). Policy-as-Code for Educational AI Agents.

[20] Indian Multilingual Prompt Injection. (2026). Hindi and Hinglish Injection Detection with 99.70% Accuracy. *Scientific Reports (Nature)*, 16, XXXXX.

[21] Corbett, A. T., & Anderson, J. R. (1994). Knowledge Tracing: Modeling the Acquisition of Procedural Knowledge. *User Modeling and User-Adapted Interaction*, 4(4), 253–278. https://doi.org/10.1007/BF01099821

[22] Venable, J., Pries-Heje, J., & Baskerville, R. (2016). FEDS: A Framework for Evaluation in Design Science Research. *European Journal of Information Systems*, 25(1), 77–89. https://doi.org/10.1057/ejis.2014.36

---

## Appendix A: LSM YAML Schema

```yaml
course_id: string          # unique course identifier (required)
name: string               # human-readable name (required)
description: string        # course description
default_language: string   # fallback language (default: "en")
languages: [string]        # supported language codes
tiers: [T1, T2, T3, T4]   # scaffold tiers (always T1–T4)
topics: [string]           # curriculum topics
matrix:                    # the core policy
  <language_code>:
    T1: boolean
    T2: boolean
    T3: boolean
    T4: boolean
escalation:
  on_adversarial_intent: warn | tighten | escalate | block
  on_leakage: rewrite | escalate | block
  on_policy_violation: rewrite | escalate | block
```

## Appendix B: System Prompt Template

```
You are TL-Guard, a multilingual tutoring buddy.
Translanguaging is welcome: students may mix languages.
Never punish or shame language mixing.
Stay within the authorized scaffold tier and response language.

Course: {course}. Concept: {concept}.
Authorized scaffold tier: {tier}. {tier_instruction}
{language_instruction}
```

## Appendix C: Supported Language Detection Patterns

**Table 8.** Language detection features.

| Language | Script Detection | Keyword Cue Examples |
|---|---|---|
| English | Latin without Devanagari/Bengali | what, how, explain, loop, function |
| Hindi | Devanagari (U+0900–U+097F) | kya, hai, matlab, samjhao, batao |
| Bengali | Bengali script (U+0980–U+09FF) | ki, kore, bolo, bujhte, amake |
| Spanish | Latin + diacritics (á, é, ñ, ¿, ¡) | que, como, explicame, ayuda |
| Mixed | Multiple scripts simultaneously | Devanagari + Latin → Hinglish |

## Appendix D: Intent Classification Patterns

**Table 9.** Multilingual adversarial and clarification patterns.

| Category | Language | Pattern |
|---|---|---|
| Adversarial | English | "full solution please", "just give me the answer" |
| Adversarial | Hindi | "पूरा कोड दे दो", "सीधा जवाब" |
| Adversarial | Bengali | "সম্পূর্ণ উত্তর" |
| Adversarial | Spanish | "dame la respuesta completa" |
| Legitimate | English | "what does X mean", "explain in simple" |
| Legitimate | Hindi | "समझाओ", "मतलब" |
| Legitimate | Bengali | "বোঝাও" |
| Legitimate | Spanish | "explícame" |
