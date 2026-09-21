# Research Plans: Two Shortlisted Topics

**Prepared:** September 2026  
**Supervisor review:** Pending  
**Connection to broader research:** Both papers extend the EduHarness pedagogical-harness paradigm into the multilingual dimension, addressing distinct but complementary research questions.

---

## Email-Ready Abstracts (for supervisor)

### Topic 1 — Simple Abstract

**Title:** Cross-Lingual Conversational Risk Accumulation for Pedagogical Safety: A Harness-Based Approach

AI tutors are increasingly used by multilingual students, but current safety checks mostly look at one message at a time and mainly work in English. Our work studies a new problem: risk that builds up across a conversation when students switch languages (for example, asking in English and then again in Hindi to get the full answer). We call this Cross-Lingual Conversational Risk Accumulation (XL-CRA). We will build a harness-based system that tracks this risk over the full tutoring session and steps in early—by tightening hints, limiting language switches, or escalating to a teacher—before the tutor leaks answers or breaks scaffolding. The contribution is a new threat model, a detection framework, and a multilingual tutoring safety benchmark.

---

### Topic 2 — Simple Abstract

**Title:** Agentic AI as a Guardrailed Multilingual Buddy: Translanguaging Support Under Pedagogical Safety Constraints

Many students learn better when they can mix languages (translanguaging), and recent work shows AI can act as a “multilingual buddy.” But today’s tools are mostly chatbots: they reply in any language without deciding *how much help* to give, *in which language*, or *whether that help is pedagogically safe*. We propose TL-Guard — an **agentic** AI buddy. Unlike a chatbot that only generates text, our agent **perceives** the student’s language and mastery, **decides** the right scaffold (hint vs explanation vs solution), **checks** teacher-defined safety rules, **acts** (respond, rewrite, or withhold), and **escalates** to a teacher when needed — while still supporting legitimate language mixing. Teachers configure which help levels are allowed in which languages. The contribution is a safe, goal-driven multilingual tutoring agent grounded in translanguaging theory, not just a multilingual chat interface.

### Topic 2 — What “Agentic” Means Here (for email / discussion)

In this topic, **agentic** does **not** mean a free multi-agent swarm. It means the AI is a **goal-driven tutoring agent** with a closed decision loop, not a passive LLM chatbot:

1. **Perceive** — Detect language(s) used, student mastery (BKT), and whether the switch looks like learning help or answer-seeking.
2. **Decide** — Choose scaffold tier and response language using the Language–Scaffold Matrix (teacher policy).
3. **Act** — Deliver a hint / explanation / rewrite / block under pedagogical constraints.
4. **Reflect / escalate** — Post-check for leakage across languages; if unsafe, escalate to the teacher queue.
5. **Remember** — Carry learner state and policy across turns (session memory), so each reply depends on history, not only the last message.

So the novelty is: **agentic tutoring behaviour + translanguaging support + pedagogical guardrails inside the agent loop**, together. Existing “multilingual buddy” work (e.g. KiKo-Prim) uses ChatGPT as a helper but without this agent loop or formal safety policy.

---

## How the Two Papers Relate (But Stay Distinct)

| Dimension | Paper 1 (Cross-Lingual CRA) | Paper 2 (Guardrailed Multilingual Buddy) |
|-----------|------------------------------|------------------------------------------|
| **Core question** | Does language-switching *create* new risk trajectories that existing guardrails miss? | Can an AI buddy *safely support* translanguaging without undermining scaffolding? |
| **Framing** | Adversarial / Red-team / Safety evaluation | Constructive / Pedagogical design / Learning support |
| **Primary contribution** | A new *threat model* + *detection framework* | A new *system architecture* + *design principles* |
| **Theory base** | Conversational Risk Accumulation (CRA) + cross-lingual safety alignment | Translanguaging pedagogy (García et al.) + pedagogical leakage theory |
| **Evaluation focus** | Attack success rates, detection latency, missed violations | Learning outcomes, translanguaging quality, scaffolding integrity |
| **Shared infrastructure** | Complementary research themes; TL-Guard (Paper 2) is an independent agent — not an EduHarness dependency |

Paper 1 asks: *"What goes wrong when students switch languages during tutoring?"*  
Paper 2 asks: *"How do we build a system that lets students switch languages safely?"*

---
---

# PAPER 1

## Cross-Lingual Conversational Risk Accumulation for Pedagogical Safety: A Harness-Based Approach

### Simple Abstract (email version)

AI tutors are increasingly used by multilingual students, but current safety checks mostly look at one message at a time and mainly work in English. Our work studies a new problem: risk that builds up across a conversation when students switch languages (for example, asking in English and then again in Hindi to get the full answer). We call this Cross-Lingual Conversational Risk Accumulation (XL-CRA). We will build a harness-based system that tracks this risk over the full tutoring session and steps in early—by tightening hints, limiting language switches, or escalating to a teacher—before the tutor leaks answers or breaks scaffolding. The contribution is a new threat model, a detection framework, and a multilingual tutoring safety benchmark.

---

### 1. Existing Research and Related Work

The literature relevant to this topic spans three distinct research streams that have not yet been integrated.

#### 1.1 Conversational Risk Accumulation (CRA) in LLMs

Recent work has established that multi-turn conversations create *compositional* safety risks invisible to turn-level filters:

- **CRA Framework** (arXiv, July 2026): Formalizes Conversational Risk Accumulation through three trajectory signals — semantic drift, information accumulation graphs, and compliance gradients — fused into a scalar CRA score. Benchmarked on CRA-Bench (1,200 eight-turn English sessions). *Limitation: English-only; general-purpose LLM, not educational.*

- **Crescendo Attack** (Russinovich et al., USENIX Security 2025): Demonstrates that benign-seeming turns can gradually escalate a conversation toward prohibited content, achieving 29–71% higher jailbreak success than single-turn attacks across GPT-4 and Gemini. *Limitation: English-only; no pedagogical dimension.*

- **Speak Out of Turn** (Li et al., arXiv 2024): Decomposes malicious queries into individually harmless sub-questions across turns, then combines prior responses. Shows that turn-level alignment succeeds but session-level alignment fails. *Limitation: English-only, general safety.*

- **Conversational Complexity for Risk** (EPJ Data Science, 2025): Proposes Conversational Length (CL) and Conversational Complexity (CC, approximated via Kolmogorov complexity) as risk assessment measures. Journal-published (Springer). *Limitation: Risk measurement only; no mitigation; English-only.*

- **Recast** (arXiv, July 2026): Forecasts trajectory-level safety risks before violations emerge, detecting 88.3% of violations approximately 2.41 turns early. *Limitation: English-only; no educational application.*

- **TRACES** (arXiv, May 2026): Uses representation-based proactive auditing with latent mechanism banks for trajectory-state modeling. *Limitation: Agent-focused, not conversation-focused; English-only.*

- **TemporalGuard** (Springer, SAIV 2026): Applies past-time linear temporal logic (ptLTL) to model conversation traces as formal execution traces with Boolean grounding. *Limitation: No multilingual evaluation; general conversations, not tutoring.*

#### 1.2 Multilingual and Cross-Lingual LLM Safety

A parallel body of work demonstrates that LLM safety degrades dramatically outside English:

- **MultiJail** (Deng et al., 2024): Low-resource languages show approximately 3× the rate of unsafe content compared to high-resource languages. Intentional multilingual prompting achieves 80.92% unsafe output on ChatGPT. Proposes the SELF-DEFENSE framework for multilingual safety fine-tuning.

- **CSRT: Code-Switching Red-Teaming** (ACL 2025): Intra-sentence code-switching achieves 46.7% higher attack success rate than standard English red-teaming across 10 state-of-the-art LLMs. Discovers unintended correlation between language resource availability and safety alignment.

- **XSAFETY** (2024): First multilingual safety benchmark across 14 languages and 14 safety categories. Proposes XLingPrompt: "Please think in English and then generate the response in the original language" as a mitigation strategy.

- **Multilingual Blending** (ResearchGate, 2025): Systematic review of ~300 publications showing English-centric bias in safety research; mixed-language prompts intensify harmful query impact.

- **MULBERE** (ACL WiNLP 2025): Multilingual jailbreak robustness via targeted latent adversarial training across 9 languages. Reduces jailbreak success by 75%.

- **Indian Multilingual Prompt Injection** (Scientific Reports / Nature, 2026): First study of prompt injection in Hindi and Hinglish (code-mixed Hindi-English). Creates a 4,000-prompt dataset and achieves 99.70% detection accuracy with a hybrid classifier.

#### 1.3 Pedagogical Safety in AI Tutoring

A third stream addresses safety specific to educational contexts:

- **SafeTutors** (ACL ARR 2026): Benchmark showing pedagogical harm surges from 17.7% (single-turn) to 77.8% (multi-turn) across mathematics, physics, and chemistry. 11 harm dimensions, 48 sub-risks. *Limitation: English-only; no cross-lingual evaluation.*

- **SHAPE** (ACL 2026): Formalizes pedagogical jailbreaks (answer-inducing prompts), proposes graph-augmented tutoring pipeline using knowledge-mastery graphs. 9,087 student-question pairs in linear algebra. *Limitation: English-only.*

- **Auditable Release Control** (arXiv, August 2026): Formalizes pedagogical leakage as state- and action-dependent unauthorized disclosure. Introduces five disclosure contracts with deterministic + semantic verification. *Limitation: English-only; no multi-turn accumulation analysis.*

- **Answer Leakage Robustness** (Zhao et al., ACL 2026): Evaluates LLM tutors under adversarial student attacks using 6 groups of adversarial techniques. Proposes fine-tuned adversarial student agents as standardized benchmarks. *Limitation: English-only.*

- **Simulating LLM-to-LLM Multilingual Math Tutoring** (arXiv, June 2025): Finds higher answer leakage rates in low-resource languages (Thai, Swahili >2%), showing that pedagogical safety degrades cross-linguistically. *This is the closest existing work to our intersection, but it only measures leakage rates — it does not model risk accumulation or provide a harness-based mitigation.*

#### 1.4 Harness Engineering and Guardrail Systems

- **SafeHarness** (arXiv, April 2026): Lifecycle-integrated security architecture with four defense layers (adversarial context filtering, tiered causal verification, privilege-separated tool control, safe rollback). Reduces unsafe behavior by ~38%. *Limitation: General agent deployment, not educational.*

- **LlamaFirewall** (Meta, May 2025): Open-source guardrail framework with PromptGuard 2, Agent Alignment Checks, and CodeShield. *Limitation: No pedagogical awareness; no multilingual-specific components.*

- **NeMo Guardrails** (NVIDIA, 2024+): YAML-based policy engine with multilingual content safety refusal messages in 9 languages. *Limitation: Content safety only, not pedagogical safety.*

---

### 2. Research Gap

**The gap exists at the intersection of three well-studied areas:**

| Studied Area | What Exists | What's Missing |
|---|---|---|
| CRA / Multi-turn risk | CRA Framework, Crescendo, TRACES, Recast — all English-only, general-purpose | CRA in cross-lingual settings; CRA in educational contexts |
| Cross-lingual LLM safety | MultiJail, CSRT, XSAFETY, MULBERE — all turn-level; general safety | Trajectory-level cross-lingual risk; pedagogical risk specifically |
| Pedagogical safety | SafeTutors, SHAPE, Auditable Release Control — all English-only | Cross-lingual pedagogical safety; risk accumulation in tutoring |

**Specific gap statement:** No existing work models how language-switching within a tutoring session creates *trajectory-level pedagogical risk accumulation* — where individually safe code-switched turns compose into answer disclosure, scaffolding collapse, or misconception reinforcement — nor proposes a harness-based detection and mitigation framework for this threat class.

The closest work (Simulating LLM-to-LLM Multilingual Tutoring, 2025) measures per-turn leakage rates across languages but does not:
- Model cumulative risk across the session trajectory
- Detect cross-lingual crescendo-style escalation patterns
- Provide a runtime harness that intervenes when accumulated risk exceeds a threshold
- Differentiate between pedagogical risk types (leakage vs. misconception vs. scaffolding collapse)

---

### 3. Proposed Research Direction

We propose **Cross-Lingual Conversational Risk Accumulation (XL-CRA)**: a framework that extends the CRA paradigm into multilingual pedagogical tutoring sessions by introducing:

1. **Language-aware trajectory signals** that detect when language switches coincide with semantic drift toward prohibited disclosure, scaffolding degradation, or misconception reinforcement.
2. **A pedagogical risk taxonomy** specific to cross-lingual tutoring (answer leakage via translation, scaffolding collapse via language mismatch, conceptual confusion via false cognates, exam-mode bypass via language switch).
3. **A harness-based mitigation pipeline** that computes a per-session XL-CRA score and triggers graded interventions (scaffold tightening, language pinning, teacher escalation) when thresholds are exceeded.

---

### 4. Research Objectives

- **RO1:** Characterize and taxonomize the cross-lingual risk accumulation patterns that arise in multilingual AI tutoring sessions.
- **RO2:** Design and implement XL-CRA, a session-layer framework that computes trajectory-level pedagogical risk across language-switched turns.
- **RO3:** Construct XL-CRA-Bench, a benchmark dataset of multilingual tutoring sessions with annotated risk trajectories.
- **RO4:** Evaluate whether harness-based intervention (scaffold tightening, language pinning) reduces cross-lingual risk accumulation compared to turn-level-only defenses.

---

### 5. Key Research Questions

- **RQ1:** What types of cross-lingual risk accumulation patterns emerge in multilingual AI tutoring sessions, and how do they differ from monolingual risk patterns? *(Characterization)*
- **RQ2:** Does language-switching amplify pedagogical risk accumulation (answer leakage, scaffolding failure, misconception reinforcement) compared to monolingual sessions of equivalent length? *(Quantification)*
- **RQ3:** Can trajectory-level cross-lingual signals (language entropy, cross-lingual semantic drift, translation-induced compliance shift) predict pedagogical safety violations before they manifest? *(Early detection)*
- **RQ4:** How effective is a harness-based intervention strategy (graded response: warn → tighten scaffold → pin language → escalate) compared to (a) no guardrail, (b) turn-level-only guardrails, and (c) English-translation-proxy defense? *(Mitigation)*

---

### 6. Proposed Methodology

**Design:** Mixed-methods evaluation combining simulated red-team attacks with controlled tutoring experiments.

**Phase 1 — Threat Characterization (Qualitative + Quantitative)**
- Deploy LLM tutors (GPT-4o, Llama 3.1 8B, Qwen 2.5 7B) across three language pairs: English–Hindi, English–Bengali, English–Spanish.
- Use automated adversarial student agents that employ five cross-lingual attack strategies:
  - *Language-switch leakage:* Ask for a hint in L1, then repeat the question in L2 to extract the answer.
  - *Translation-proxy bypass:* Translate a blocked English prompt into a low-resource language.
  - *Code-mixing escalation:* Gradually increase L2 vocabulary density to erode safety alignment.
  - *False-cognate confusion:* Use domain terms that have different meanings across languages.
  - *Script-switch evasion:* Alternate between Latin and Devanagari/Bangla script within a session.
- Record full session traces with per-turn language identification, pedagogical action labels, and risk annotations.

**Phase 2 — Framework Development (Engineering)**
- Extend EduHarness's verification pipeline with three new trajectory signals:
  - **S₁: Cross-Lingual Semantic Drift** — Embed each turn in a shared multilingual space (e.g., multilingual-e5); compute cosine drift from the session anchor, weighted by language-switch events.
  - **S₂: Pedagogical Information Accumulation Graph (P-IAG)** — Track which answer components have been disclosed across languages; flag when cross-lingual disclosures compose into a complete answer.
  - **S₃: Scaffold Compliance Gradient** — Measure whether the tutor's scaffold tier is degrading over cross-lingual turns (e.g., starting with hints in English, then giving full solutions in Hindi).
- Fuse into a scalar **XL-CRA(t) ∈ [0, 1]** score per session at each turn *t*.
- Implement four graded intervention levels triggered by XL-CRA thresholds:
  - θ₁: Log + tighten scaffold tier by one level
  - θ₂: Pin the session to the current language (disable further switching)
  - θ₃: Escalate to teacher queue with the cross-lingual risk trace
  - θ₄: Block response and request teacher review

**Phase 3 — Benchmark Construction**
- Generate **XL-CRA-Bench**: 1,500+ tutoring sessions (500 per language pair) with:
  - 5 risk categories × 3 language pairs × 3 difficulty levels
  - Matched monolingual controls for each cross-lingual session
  - Per-turn annotations: language ID, risk label, scaffold tier, disclosed answer components
- Release as a public resource.

**Phase 4 — Evaluation**
- Compare XL-CRA against baselines:
  - B0: No guardrail
  - B1: Turn-level content safety (LlamaGuard/NeMo)
  - B2: English CRA Framework (original, monolingual)
  - B3: XLingPrompt ("think in English") defense
  - B4: XL-CRA (our framework)
- Metrics: Session-level violation rate, turns-to-detection, false positive rate (on benign multilingual sessions), scaffold integrity score, leakage rate per language.

---

### 7. Proposed Framework Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   XL-CRA Session Layer                      │
│                                                             │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │ S₁: XL       │  │ S₂: P-IAG     │  │ S₃: Scaffold     │  │
│  │ Semantic Drift│  │ Ped. Info     │  │ Compliance       │  │
│  │ Monitor      │  │ Accumulation  │  │ Gradient         │  │
│  └──────┬───────┘  └──────┬────────┘  └──────┬───────────┘  │
│         └─────────────┬───┘───────────────────┘             │
│                       ▼                                     │
│              ┌────────────────┐                              │
│              │  XL-CRA Score  │ → threshold → intervention   │
│              │  fusion layer  │                              │
│              └────────────────┘                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ wraps
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               EduHarness Turn Pipeline                      │
│  Student → Lang ID → Verify → LLM → Post-Check → Output    │
│              ↑                                     │        │
│              └── Language-aware scaffold policy ────┘        │
└─────────────────────────────────────────────────────────────┘
```

Key architectural contributions:
- The XL-CRA session layer sits *above* the existing turn-level pipeline and provides trajectory-level monitoring.
- Language identification is integrated at the input stage, and language-switch events become first-class signals.
- The post-check is extended with cross-lingual leakage detection (checking whether the LLM disclosed in L2 what was withheld in L1).

---

### 8. Expected Novelty and Contributions

| # | Contribution | Supporting Evidence |
|---|---|---|
| **C1** | **First formalization of cross-lingual CRA in educational settings** — We define XL-CRA as the compositional accumulation of pedagogical risk across language-switched tutoring turns. | CRA Framework (2026) works only in English; SafeTutors (2026) shows multi-turn pedagogical harm but only in English; CSRT (2025) shows code-switching attacks but not in tutoring. No intersection exists. |
| **C2** | **A cross-lingual pedagogical risk taxonomy** — Five risk patterns specific to language-switching in tutoring (leakage-via-translation, code-mixing escalation, false-cognate confusion, script-switch evasion, scaffold collapse via language mismatch). | MultiJail (2024) and CSRT (2025) document cross-lingual attacks but not pedagogical risk types. SafeTutors (2026) defines 48 pedagogical sub-risks but all in English. |
| **C3** | **XL-CRA-Bench** — A public benchmark of 1,500+ annotated multilingual tutoring sessions with trajectory-level risk labels. | CRA-Bench (2026) covers English general-purpose; SafeTutors dataset is English tutoring. No cross-lingual tutoring risk benchmark exists. |
| **C4** | **A harness-based graded intervention pipeline** for cross-lingual pedagogical risk, with configurable thresholds and four escalation levels. | Existing mitigations are either turn-level (LlamaGuard, NeMo) or monolingual trajectory-level (CRA Framework). No harness provides graded multilingual pedagogical intervention. |

---

### 9. Experimental Design and Evaluation

| Experiment | What It Measures | Design |
|---|---|---|
| **E1: Risk characterization** | Prevalence and types of cross-lingual pedagogical risk | 3 models × 3 language pairs × 5 attack types × 50 sessions = 2,250 sessions. Manual annotation of a random 20% subset. |
| **E2: Amplification test** | Whether language-switching amplifies risk vs. monolingual baseline | Matched-pair design: each cross-lingual session has a monolingual control. Compare per-session violation rates. |
| **E3: Early detection** | XL-CRA's ability to detect violations before they manifest | Measure turns-to-detection (TTD) across all benchmark sessions. Compare against B1–B3 baselines. |
| **E4: Mitigation efficacy** | Whether graded intervention reduces violations while maintaining learning utility | A/B comparison across 5 conditions (B0–B4). Measure violation rate, scaffold integrity, and utility (helpfulness) trade-off. |
| **E5: Cross-model robustness** | Whether XL-CRA generalizes across model families | Test on 3 models (GPT-4o, Llama 3.1, Qwen 2.5) to confirm harness effectiveness is model-agnostic. |

---

### 10. Potential Datasets and Scenarios

- **XL-CRA-Bench** (to be constructed): 1,500 annotated multilingual tutoring sessions.
- **Adversarial prompts**: Extend EduHarness-Adv-500 with cross-lingual variants (translate each prompt into Hindi, Bengali, Spanish; create code-mixed versions).
- **Tutoring domains**: Python programming (primary, from EduHarness), mathematics (secondary), general science (tertiary).
- **Language pairs**: English–Hindi, English–Bengali, English–Spanish (covering one high-resource, one mid-resource, and one low-resource pairing from the Indian educational context).

---

### 11. Expected Outcomes

1. Empirical evidence that language-switching amplifies pedagogical risk accumulation by a quantifiable margin (hypothesized: 30–60% higher session-level violation rate than monolingual).
2. A validated XL-CRA score that predicts cross-lingual pedagogical violations 2+ turns before manifestation.
3. Demonstration that harness-based graded intervention reduces cross-lingual violations by >50% compared to no guardrail, while maintaining >80% of baseline tutoring utility.
4. A public benchmark (XL-CRA-Bench) and adversarial dataset enabling reproducible research.

---

### 12. Limitations and Future Work

**Limitations:**
- Initial evaluation uses simulated adversarial agents, not real students. Human-subject validation is necessary for ecological validity.
- Three language pairs (En-Hi, En-Bn, En-Es) do not fully represent global linguistic diversity; low-resource African and Southeast Asian languages remain untested.
- The XL-CRA score relies on multilingual sentence embeddings whose quality varies across languages.
- The harness interventions (language pinning, scaffold tightening) may reduce learning utility for legitimate translanguaging use; false positive analysis is critical.

**Future Work:**
- Extend to real classroom deployment (IRB-approved study with multilingual students).
- Investigate cross-lingual risk in voice-based tutoring (where code-switching is even more natural).
- Integrate with Paper 2's translanguaging-aware design to balance safety with legitimate multilingual learning.
- Explore whether the XL-CRA signals can be used to *improve* rather than just *constrain* multilingual tutoring (i.e., detecting when a language switch reflects genuine learning need vs. adversarial intent).

---

### 13. Proposed Abstract (academic version)

> Large language model tutors are increasingly deployed in multilingual educational settings, yet current safety evaluations and guardrails operate exclusively in English and evaluate each prompt–response pair in isolation. We identify a previously uncharacterized threat class: **cross-lingual conversational risk accumulation (XL-CRA)**, where individually safe language-switched tutoring turns compose over a session into pedagogical violations — answer disclosure via translation, scaffolding collapse through language mismatch, and misconception reinforcement through false cognates. We formalize XL-CRA through three trajectory-level signals — cross-lingual semantic drift, a pedagogical information accumulation graph, and a scaffold compliance gradient — fused into a session-level risk score. We construct **XL-CRA-Bench**, a benchmark of 1,500 annotated multilingual tutoring sessions across three language pairs (English–Hindi, English–Bengali, English–Spanish) with five attack categories. We implement XL-CRA as a session layer within the EduHarness pedagogical harness and evaluate four graded intervention strategies against three baselines across three LLM families. Results show that cross-lingual sessions exhibit [X]% higher pedagogical violation rates than monolingual controls, that XL-CRA detects violations [Y] turns before manifestation, and that harness-based intervention reduces violations by [Z]% while maintaining [W]% of tutoring utility. To our knowledge, this is the first framework that models trajectory-level pedagogical risk accumulation across languages and provides configurable, harness-based mitigation.

---

### 14. Suggested Paper Structure

1. **Introduction** (1.5 pages)
2. **Related Work** (2 pages)
3. **XL-CRA Framework** (3 pages)
4. **XL-CRA-Bench** (1.5 pages)
5. **Experimental Setup** (1.5 pages)
6. **Results and Analysis** (2.5 pages)
7. **Discussion** (1.5 pages)
8. **Conclusion and Future Work** (0.5 pages)
9. **References**
10. **Appendices**

**Target venues:** *Computers & Education* (Elsevier), *User Modeling and User-Adapted Interaction* (Springer), *ACM Transactions on Interactive Intelligent Systems*, or *IEEE Transactions on Learning Technologies*.

---
---
---

# PAPER 2

## Agentic AI as a Guardrailed Multilingual Buddy: Translanguaging Support Under Pedagogical Safety Constraints

### Simple Abstract (email version)

Many students learn better when they can mix languages (translanguaging), and recent work shows AI can act as a “multilingual buddy.” But today’s tools are mostly chatbots: they reply in any language without deciding *how much help* to give, *in which language*, or *whether that help is pedagogically safe*. We propose TL-Guard — an **agentic** AI buddy. Unlike a chatbot that only generates text, our agent **perceives** the student’s language and mastery, **decides** the right scaffold (hint vs explanation vs solution), **checks** teacher-defined safety rules, **acts** (respond, rewrite, or withhold), and **escalates** to a teacher when needed — while still supporting legitimate language mixing. Teachers configure which help levels are allowed in which languages. The contribution is a safe, goal-driven multilingual tutoring agent grounded in translanguaging theory, not just a multilingual chat interface.

### What “Agentic” Means in This Topic

In this topic, **agentic** does **not** mean a free multi-agent swarm. It means the AI is a **goal-driven tutoring agent** with a closed decision loop, not a passive LLM chatbot:

1. **Perceive** — Detect language(s) used, student mastery (BKT), and whether the switch looks like learning help or answer-seeking.
2. **Decide** — Choose scaffold tier and response language using the Language–Scaffold Matrix (teacher policy).
3. **Act** — Deliver a hint / explanation / rewrite / block under pedagogical constraints.
4. **Reflect / escalate** — Post-check for leakage across languages; if unsafe, escalate to the teacher queue.
5. **Remember** — Carry learner state and policy across turns (session memory), so each reply depends on history, not only the last message.

So the novelty is: **agentic tutoring behaviour + translanguaging support + pedagogical guardrails inside the agent loop**, together. Existing “multilingual buddy” work (e.g. KiKo-Prim) uses ChatGPT as a helper but without this agent loop or formal safety policy.

---

### 1. Existing Research and Related Work

This topic draws from four research streams that have developed largely independently.

#### 1.1 AI as a "Multilingual Buddy" in Education

- **KiKo-Prim: AI-Supported Translanguaging in Primary School** (Springer, *Technology, Knowledge and Learning*, 2026): The seminal study coining "multilingual buddy." Analyzes 462 conversational turns showing ChatGPT supporting vocabulary retrieval, explanation refinement, and multilingual artifact production in Grades 3–4. Finds that productive AI use depends on guided prompting, teacher facilitation, and subject-specific integration. *Limitation: No formal guardrails; no safety evaluation; no agentic architecture.*

- **Walter: AI-Powered Learning Buddy** (*Asia Pacific Journal of Educators and Education*, 2026): A Gen-AI buddy for non-native English speakers using sociocultural theory (MKO within ZPD). Shows statistically significant improvement in oral presentation scores (p < .001, d = 0.75). *Limitation: English-only; no multilingual support; no safety constraints.*

- **AI-Mediated Translanguaging in Pakistan** (CJSSR, 2026): Explores AI-mediated translanguaging in multilingual EFL classrooms. Confirms pedagogical value but highlights risks: incorrect feedback, over-reliance, uncontrolled language-switching. *Limitation: No technical architecture; no guardrail design.*

- **Acharjo / Regionalized StudentGPT** (ISJEM, 2025): Curriculum-aligned multilingual tutoring for Bengali and Assamese using GPT-3.5 with RAG and curriculum regularization. Shows 22% improvement in pedagogical accuracy. Compliant with IEEE 7000-2021. *Limitation: No real-time safety guardrails; no translanguaging theory.*

- **GurukulAI** (arXiv, July 2026): Hindi–English NCERT-aligned tutoring using LLaMA 3.1 8B with RAG. Open-source. *Limitation: Bilingual only; no guardrails; no translanguaging framework.*

- **7S Samiti** (blog / deployment report, 2025): Production-deployed AI tutor for rural India with voice-first interface, code-switching Hindi-English support, and hallucination controls via RAG. *Limitation: Engineering report, not research paper; no formal evaluation; no guardrail architecture.*

- **OAMTS** (Zenodo preprint, 2026): Offline multilingual tutoring architecture for rural education. Conceptual design only. *Limitation: No implementation; no safety component.*

#### 1.2 Translanguaging Theory and Pedagogy

- **García, Johnson & Seltzer (2017)**: Define the canonical translanguaging pedagogy framework: **Stance** (ideological commitment to multilingualism as resource), **Design** (purposeful planning of instruction leveraging full linguistic repertoires), and **Shifts** (moment-to-moment instructional adjustments). This is the theoretical foundation.

- **García & Li Wei (2014)**: Establish translanguaging as a theory of language where bilingual speakers deploy a single integrated linguistic repertoire, not two separate language systems. Critical for understanding why AI tutors should not enforce strict language separation.

- **Translanguaging in CS Education** (2020, NSF): Applies translanguaging to computational literacies, framing programming as a form of language practice where students use their full repertoires. Proposes "conversations about, with, and through code." *Limitation: No AI component; human teacher only.*

- **Translanguaging in STEM Meta-Synthesis** (MDPI *Education Sciences*, 2026): Systematic review of 20 studies. Identifies four themes: research gaps (especially in CS and math), translanguaging as syncretic practice, students as local agents, and persistent challenges from monoglossic ideologies. *Limitation: No AI or technology component.*

- **Cummins' Linguistic Interdependence Hypothesis** (1979, 2000): Foundational theory that academic language proficiency transfers across languages. Provides theoretical justification for why a tutor should support cross-lingual concept building.

#### 1.3 Pedagogical Safety in AI Tutoring

- **SafeTutors** (ACL ARR 2026): Pedagogical harm surges 17.7% → 77.8% in multi-turn. Relevant because even in English, tutors fail at scaffolding — the risk is amplified when language mixing is added.

- **SHAPE** (ACL 2026): Graph-augmented pipeline that infers prerequisite mastery and routes between instruction and problem-solving. Relevant as a model for mastery-aware routing.

- **Auditable Release Control** (arXiv, August 2026): Formalizes disclosure contracts. Relevant because a multilingual buddy needs to control *what* is disclosed *in which language* and *at what scaffold tier*.

- **Simulating LLM-to-LLM Multilingual Math Tutoring** (arXiv, June 2025): Shows higher leakage in low-resource languages. Directly relevant: the buddy must prevent leakage while supporting legitimate translanguaging.

#### 1.4 Guardrail Systems for Multilingual Education

- **NeMo Guardrails** (NVIDIA, 2024+): Supports multilingual refusal messages in 9 languages including Hindi. *Limitation: Content safety only; no pedagogical awareness; no translanguaging support.*

- **EvalGuard Education Agent** (2026): Policy-as-code blueprint for educational agents with FERPA compliance, tutoring-vs-cheating detection, and PII redaction. *Limitation: English-only; no multilingual policy.*

- **Cohorte Guardrails** (2025): Vendor-neutral YAML policy engine with allow/deny/redact/approval outcomes. *Limitation: General-purpose; no educational or multilingual specialization.*

- **Indian Multilingual Prompt Injection** (Scientific Reports, 2026): 4,000-prompt dataset for Hindi/Hinglish injection detection. 99.70% accuracy. *Relevant as a safety component for Indian multilingual buddy.*

---

### 2. Research Gap

**The gap exists at the intersection of four areas:**

| Area | What Exists | What's Missing |
|---|---|---|
| AI Multilingual Buddy | KiKo-Prim, Walter, Acharjo, GurukulAI — functional but no formal safety | Safety-guardrailed buddy that prevents pedagogical harm while supporting translanguaging |
| Translanguaging Theory | García's Stance/Design/Shifts; Cummins' Interdependence — well-established but not operationalized in AI | A computational operationalization of translanguaging pedagogy for AI agent design |
| Pedagogical Safety | SafeTutors, SHAPE, Auditable Release Control — all English-only | Pedagogical safety constraints that account for multilingual interaction patterns |
| Guardrail Systems | NeMo, EvalGuard, Cohorte — content safety and general policy | Pedagogical guardrails that enforce scaffold integrity *while supporting* translanguaging |

**Specific gap statement:** No existing system integrates translanguaging pedagogy theory (García's Stance/Design/Shifts) into the design of an AI tutoring agent with formal pedagogical safety constraints. Current multilingual AI tutors support language mixing but lack guardrails against pedagogical harm. Current guardrail systems enforce content safety but are pedagogically unaware and treat language mixing as a potential attack vector rather than a legitimate learning resource.

The result is a design tension: **safety systems view code-switching as suspicious, while translanguaging pedagogy views it as essential.** No existing architecture resolves this tension.

---

### 3. Proposed Research Direction

We propose **TL-Guard (TransLanguaging-Aware Guardrailed AI Buddy)**: an agentic AI tutoring architecture that:

1. **Operationalizes translanguaging pedagogy** (García's Stance/Design/Shifts) as computational design principles for the AI agent's behavior.
2. **Enforces pedagogical safety constraints** (scaffold integrity, leakage prevention, misconception avoidance) inside the agent loop (Decide / Act / Reflect) that is *language-aware but language-tolerant*.
3. **Distinguishes legitimate translanguaging from adversarial language-switching** through intent classification and mastery-context analysis.
4. **Supports teacher-defined multilingual policies** via YAML contracts that specify which languages are permitted, which scaffold tiers can be delivered in which languages, and when to escalate.

---

### 4. Research Objectives

- **RO1:** Operationalize García's translanguaging pedagogy framework (Stance/Design/Shifts) as design principles for AI tutoring agents.
- **RO2:** Design and implement TL-Guard, a pedagogical safety architecture that supports translanguaging while preventing leakage, misconception reinforcement, and scaffolding collapse.
- **RO3:** Define and validate a set of multilingual pedagogical policy constructs (language-scaffold matrix, translanguaging-aware disclosure contracts) that teachers can configure.
- **RO4:** Evaluate whether TL-Guard improves learning outcomes for multilingual learners compared to (a) English-only tutoring, (b) unguardrailed multilingual tutoring, and (c) safety-guardrailed English-only tutoring.

---

### 5. Key Research Questions

- **RQ1:** How can translanguaging pedagogy principles (Stance, Design, Shifts) be computationally operationalized in an agentic AI tutoring architecture? *(Design science)*
- **RQ2:** Can a language-scaffold matrix (specifying which scaffold tiers are available in which languages) maintain pedagogical safety while supporting legitimate translanguaging? *(Policy design)*
- **RQ3:** Can the agent’s Decide + Reflect stages distinguish between legitimate translanguaging and adversarial language-switching in real-time, using mastery context and interaction history? *(Classification)*
- **RQ4:** Does a guardrailed multilingual buddy improve learning outcomes (concept mastery, engagement, satisfaction) for multilingual learners compared to English-only and unguardrailed multilingual baselines? *(Efficacy)*
- **RQ5:** What are the failure modes of TL-Guard, and under what conditions does the guardrail inappropriately suppress legitimate translanguaging? *(Boundary analysis)*

---

### 6. Proposed Methodology

**Design:** Design Science Research (DSR) following the FEDS evaluation framework (Venable et al., 2016).

**Phase 1 — Theoretical Operationalization**
- Map García's three-pronged translanguaging framework to computational constructs:

| Translanguaging Principle | Computational Operationalization |
|---|---|
| **Stance** (multilingualism as resource) | Agent's system prompt affirms multilingual input; language-switch events are logged as *features*, not *anomalies*; no penalty for using L2 |
| **Design** (purposeful multilingual instruction planning) | **Language-Scaffold Matrix (LSM):** A YAML-defined policy specifying which scaffold tiers (pseudocode hint, conceptual explanation, worked example, full solution) are available in which languages. Teachers configure this per course/topic. |
| **Shifts** (moment-to-moment adjustments) | **Adaptive Language Policy Engine:** At each turn, the agent evaluates (a) the student's language choice, (b) their current mastery, (c) the scaffold tier being delivered, and (d) whether the language choice enables or undermines the pedagogical goal. Adjusts response language accordingly. |

**Phase 2 — Architecture Design and Implementation**
- Build TL-Guard as an independent agentic tutoring system with three core components:

1. **Language Intent Classifier:** Determines whether a language switch is:
   - *Legitimate translanguaging:* Student uses L2 for conceptual clarification, vocabulary retrieval, or cultural connection.
   - *Adversarial switching:* Student switches language to extract information withheld in L1.
   - *Neutral:* Student simply prefers L2 for this interaction.

2. **Translanguaging-Aware Disclosure Contracts:** Extend the Auditable Release Control framework with language-specific authorization:
   - A hint authorized in English may or may not be authorized in Hindi, depending on the LSM policy.
   - Full solutions are never available via language switch if the policy restricts them.
   - Cross-lingual paraphrase detection prevents the tutor from disclosing in L2 what it withheld in L1.

3. **Multilingual Post-Check:** Extend the post-check pipeline with:
   - Cross-lingual leakage detection
   - Scaffold consistency check
   - Cultural appropriateness check

**Phase 3 — Policy Design**
- Design the **Language-Scaffold Matrix (LSM)** as a YAML extension and validate with educators through design workshops.

**Phase 4 — Evaluation**
- **Simulated evaluation:** 5 multilingual learner personas × 3 language pairs × 4 conditions × 10 concepts × 5 turns.
- **Metrics:** Scaffolding integrity, leakage rate, translanguaging support quality, mastery trajectory, false suppression rate.

---

### 7. Proposed Framework Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TL-Guard Architecture                    │
│                                                             │
│  Student (multilingual input)                               │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────┐                                       │
│  │  Language Intent  │ → legitimate / adversarial / neutral  │
│  │  Classifier       │                                       │
│  └────────┬─────────┘                                       │
│           ▼                                                 │
│  ┌──────────────────┐    ┌──────────────────────────┐       │
│  │  Verification     │◀───│ Language-Scaffold Matrix  │       │
│  │  Gate (Layer 1)   │    │ (YAML policy)            │       │
│  └────────┬─────────┘    └──────────────────────────┘       │
│           ▼                                                 │
│  ┌──────────────────┐    ┌──────────────────────────┐       │
│  │  LLM Executor     │◀───│ TL-Aware Disclosure      │       │
│  │  (constrained     │    │ Contract                 │       │
│  │   prompt in L)    │    └──────────────────────────┘       │
│  └────────┬─────────┘                                       │
│           ▼                                                 │
│  ┌──────────────────┐                                       │
│  │  Multilingual     │ → XL leakage / scaffold consistency  │
│  │  Post-Check       │ → cultural appropriateness           │
│  └────────┬─────────┘                                       │
│     ┌─────┼──────┬──────┐                                   │
│     ▼     ▼      ▼      ▼                                   │
│   Safe  Rewrite  Escalate  Block                            │
│                                                             │
│  Teacher: configure LSM + review escalations                │
└─────────────────────────────────────────────────────────────┘
```

---

### 8. Expected Novelty and Contributions

| # | Contribution | Supporting Evidence |
|---|---|---|
| **C1** | **First computational operationalization of translanguaging pedagogy (Stance/Design/Shifts) for AI agent design.** | García et al. (2017) define the framework for human teachers. KiKo-Prim (2026) uses ChatGPT as a buddy but without formalizing the pedagogy computationally. |
| **C2** | **The Language-Scaffold Matrix (LSM):** A teacher-configurable YAML policy construct that specifies which pedagogical scaffold tiers are available in which languages. | NeMo Guardrails has multilingual refusal messages but no scaffold-level language policy. No existing system offers per-tier, per-language pedagogical control. |
| **C3** | **Translanguaging-aware disclosure contracts** that extend the Auditable Release Control paradigm with language-specific authorization. | ARC (2026) defines disclosure contracts but assumes monolingual interaction. |
| **C4** | **A Language Intent Classifier** that distinguishes legitimate translanguaging from adversarial language-switching using mastery context and interaction history. | CSRT (2025) shows code-switching as an attack vector. García (2017) shows it as a learning resource. No system classifies the intent of a language switch in tutoring. |
| **C5** | **Empirical evidence** that guardrailed translanguaging support improves learning outcomes compared to both English-only and unguardrailed multilingual baselines. | KiKo-Prim (2026) provides exploratory evidence for the buddy concept. No controlled study compares guardrailed vs. unguardrailed multilingual AI tutoring. |

---

### 9. Experimental Design and Evaluation

| Experiment | What It Measures | Design |
|---|---|---|
| **E1: LSM policy validation** | Whether the Language-Scaffold Matrix correctly enforces per-tier, per-language disclosure | 100 test scenarios × 3 languages × 5 tiers = 1,500 checks. Measure policy compliance rate. |
| **E2: Intent classification** | Accuracy of distinguishing legitimate translanguaging from adversarial switching | Balanced dataset of 500 legitimate + 500 adversarial language-switch instances. Precision, recall, F1. |
| **E3: Comparative tutoring** | Learning outcomes across 4 conditions | 5 personas × 3 language pairs × 4 conditions × 10 concepts × 5 turns. Measure mastery gain, leakage rate, scaffold integrity, translanguaging quality. |
| **E4: False suppression analysis** | How often TL-Guard incorrectly blocks legitimate translanguaging | Subset of E3 sessions labeled by human annotators. Measure false positive rate on legitimate L2 use. |
| **E5: Teacher usability** | Whether teachers can understand and configure the LSM | 5 multilingual educators attempt to configure LSM for their courses. Task completion rate, time, SUS score. |

---

### 10. Potential Datasets and Scenarios

- **Multilingual tutoring sessions** (to be constructed): Simulated sessions with multilingual student personas using TL-Guard.
- **Language pairs:** English–Hindi, English–Bengali, English–Spanish (aligned with Paper 1 for cross-paper comparability).
- **Domains:** Python programming (primary), mathematics (secondary).
- **Existing resources to leverage:** Indian multilingual prompt injection dataset, GurukulAI NCERT dataset, KiKo-Prim interaction data (if available).

---

### 11. Expected Outcomes

1. A formal mapping of translanguaging pedagogy principles to computational AI agent design constructs.
2. The Language-Scaffold Matrix (LSM) as a practical, teacher-configurable YAML policy artifact.
3. Empirical evidence that TL-Guard maintains scaffold integrity (>95% policy compliance) while supporting legitimate translanguaging (>90% instances correctly permitted).
4. Evidence that guardrailed multilingual tutoring produces higher mastery gains than English-only tutoring for multilingual learners, while maintaining equivalent safety.
5. Design principles for building safe multilingual AI educational agents.

---

### 12. Limitations and Future Work

**Limitations:**
- Simulated evaluation with persona-driven learners; real-student validation needed.
- The Language Intent Classifier may struggle with ambiguous cases.
- Three language pairs provide limited linguistic diversity.
- Cultural appropriateness checking is limited to surface-level heuristics.
- Assumes access to multilingual LLMs with reasonable quality in all supported languages.

**Future Work:**
- Real classroom deployment study with IRB approval.
- Voice-based translanguaging buddy.
- Extension to more language pairs (Tamil, Telugu, Mandarin, etc.).
- Integration with Paper 1's XL-CRA framework.
- Adaptive LSM policies that learn from teacher corrections over time.

---

### 13. Proposed Abstract (academic version)

> Multilingual learners benefit from translanguaging — the fluid use of their full linguistic repertoire — yet current AI tutoring systems either enforce monolingual interaction or permit unguardrailed language mixing that degrades pedagogical safety. We propose **TL-Guard**, an agentic AI tutoring architecture that operationalizes García et al.'s translanguaging pedagogy framework (Stance, Design, Shifts) as computational design principles while enforcing pedagogical safety constraints inside a five-stage agentic decision loop (Perceive → Decide → Act → Reflect → Remember). Central to TL-Guard is the **Language-Scaffold Matrix (LSM)**, a teacher-configurable YAML policy that specifies which pedagogical scaffold tiers (pseudocode hint, conceptual explanation, worked example, full solution) are available in which languages, enabling controlled translanguaging rather than unconstrained language mixing. A **Language Intent Classifier** distinguishes legitimate translanguaging (driven by learning need) from adversarial language-switching (driven by extraction intent) using mastery context and interaction history. **Translanguaging-aware disclosure contracts** extend the auditable release control paradigm with language-specific authorization, preventing the AI from disclosing in one language what the pedagogical contract withholds in another. We evaluate TL-Guard across three language pairs (English–Hindi, English–Bengali, English–Spanish) in Python programming and mathematics tutoring, comparing four conditions: English-only, unguardrailed multilingual, content-safety-guardrailed, and TL-Guard. Results show that TL-Guard maintains [X]% scaffold policy compliance while correctly permitting [Y]% of legitimate translanguaging instances, achieving [Z]% higher mastery gains than English-only tutoring for multilingual learners. To our knowledge, this is the first system to integrate translanguaging pedagogy theory with formal pedagogical safety constraints in an AI tutoring agent.

---

### 14. Suggested Paper Structure

1. **Introduction** (1.5 pages)
2. **Theoretical Background** (2 pages)
3. **Operationalizing Translanguaging for AI Agents** (2 pages)
4. **TL-Guard Architecture** (2.5 pages)
5. **Experimental Design** (1.5 pages)
6. **Results** (2 pages)
7. **Discussion** (1.5 pages)
8. **Conclusion and Future Work** (0.5 pages)
9. **References**
10. **Appendices**

**Target venues:** *Computers & Education* (Elsevier), *Technology, Knowledge and Learning* (Springer), *International Journal of Artificial Intelligence in Education* (Springer), or *British Journal of Educational Technology* (Wiley).

---
---

## Cross-Reference Summary

| Element | Paper 1 (XL-CRA) | Paper 2 (TL-Guard) |
|---------|-------------------|---------------------|
| Primary theory | CRA (2026) + Cross-lingual safety | Translanguaging pedagogy (García, 2017) |
| Research type | Empirical evaluation + framework | Design science + empirical evaluation |
| Artifact | XL-CRA session layer + XL-CRA-Bench | TL-Guard architecture + LSM policy |
| Attack model | Adversarial students exploiting language switches | N/A (assumes good-faith learners, but measures accidental leakage) |
| Safety focus | Detection and mitigation of accumulated risk | Prevention by design + runtime enforcement |
| Language pairs | En–Hi, En–Bn, En–Es (shared for comparability) | En–Hi, En–Bn, En–Es (shared) |
| Domains | Python, math, general science | Python, math |
| Shared infrastructure | Complementary themes only | Independent TL-Guard agent (no EduHarness) |
| How they connect | Paper 1's XL-CRA score can be integrated as a signal in Paper 2's architecture | Paper 2's LSM policy defines the "authorized" baseline that Paper 1 monitors for violations |

---

*This document was prepared by conducting targeted literature searches across ACM Digital Library, IEEE Xplore, Springer, Elsevier (ScienceDirect), MDPI, Nature/Scientific Reports, arXiv, and ACL Anthology.*
