# Development Plan: TL-Guard

**Agentic AI as a Guardrailed Multilingual Buddy: Translanguaging Support Under Pedagogical Safety Constraints**

**Created:** September 2026
**Last Updated:** September 21, 2026
**Status:** MVP implemented (independent agent + API + UI; research evaluation phases still open)
**Project stance:** Independent codebase — TL-Guard is a **first-class agentic tutoring system**, not an EduHarness extension and not a harness wrapping a chatbot. Shared research ideas (disclosure control, pedagogical safety) may inform design, but there is no code, package, or runtime dependency on EduHarness.

---

## 1. Project Summary

TL-Guard is an agentic AI tutoring architecture that supports multilingual learners through safe, controlled translanguaging. Unlike existing multilingual chatbots that respond in any language without pedagogical awareness, TL-Guard operates as a goal-driven agent with a closed decision loop: **Perceive → Decide → Act → Reflect → Remember**. Teachers configure safety policies via a Language-Scaffold Matrix (LSM), and the system distinguishes legitimate translanguaging from adversarial language-switching in real time.

**Core tension this resolves:** Safety systems treat code-switching as suspicious. Translanguaging pedagogy treats it as essential. TL-Guard resolves this by being *language-tolerant but pedagogically strict*.

**Product surface:** A self-contained tutoring product with (1) the TL-Guard agent (Perceive→Decide→Act→Reflect→Remember), (2) a student chat UI for multilingual tutoring, and (3) a teacher UI for LSM configuration and escalation review.
---

## 2. Research Objectives

| ID | Objective |
|----|-----------|
| RO1 | Operationalize García's translanguaging framework (Stance/Design/Shifts) as computational design principles for AI tutoring agents |
| RO2 | Design and implement TL-Guard — a pedagogical safety architecture supporting translanguaging while preventing leakage, misconception reinforcement, and scaffolding collapse |
| RO3 | Define and validate multilingual pedagogical policy constructs (Language-Scaffold Matrix, translanguaging-aware disclosure contracts) that teachers can configure |
| RO4 | Evaluate whether TL-Guard improves learning outcomes for multilingual learners vs. English-only, unguardrailed multilingual, and safety-guardrailed English-only baselines |

---

## 3. Development Phases

### Phase 0: Foundation & Environment Setup
**Duration:** Weeks 1–2
**Goal:** Establish the development environment, dependencies, and project scaffolding.

| Task | Description | Deliverable |
|------|-------------|-------------|
| 0.1 | Set up independent Python project structure (src/, ui/, api/, tests/, configs/, data/, notebooks/) — no EduHarness import or submodule | Project skeleton with pyproject.toml |
| 0.2 | Set up LLM access — API keys for GPT-4o; local inference for LLaMA 3.1 8B and Qwen 2.5 7B via vLLM or Ollama | Verified inference for all 3 model families |
| 0.3 | Design and stub TL-Guard's own turn pipeline: **verify → LLM → post-check → output** (thin stubs that pass English tutoring through end-to-end) | Minimal working English tutoring session via CLI |
| 0.4 | Set up multilingual NLP tooling — language detection (fastText lid.176.bin or lingua-py), multilingual embeddings (multilingual-e5-large), tokenizers for Hindi/Bengali/Spanish | Verified language ID and embedding for all 3 language pairs |
| 0.5 | Set up experiment tracking (Weights & Biases or MLflow), logging, and reproducibility infrastructure | Tracked dummy experiment run |
| 0.6 | Literature deep-dive: read and annotate García et al. (2017), KiKo-Prim (2026), Auditable Release Control (2026), SafeTutors (2026) in full | Annotated reading notes in docs/ |
| 0.7 | Decide UI stack (recommended: FastAPI backend + Next.js or Streamlit MVP) and scaffold empty `ui/` + `api/` packages | Empty UI/API apps that start locally |

**Exit criteria:** All dependencies installed, all 3 LLMs callable, independent verify→LLM→post-check→output stub running in English, language detection + embeddings verified, UI/API scaffolds boot.

---

### Phase 1: Theoretical Operationalization
**Duration:** Weeks 3–5
**Goal:** Map García's translanguaging pedagogy to formal computational constructs.

| Task | Description | Deliverable |
|------|-------------|-------------|
| 1.1 | Formalize Stance → System Prompt Design: Draft system prompts that affirm multilingual input, log language-switch events as features (not anomalies), and avoid penalizing L2 usage | System prompt templates for TL-Guard agent |
| 1.2 | Formalize Design → Language-Scaffold Matrix (LSM) schema: Define the YAML schema specifying which scaffold tiers (pseudocode hint, conceptual explanation, worked example, full solution) are available in which languages per course/topic | `lsm_schema.yaml` + 3 example LSM configs (Python, math, science) |
| 1.3 | Formalize Shifts → Adaptive Language Policy Engine spec: Define the per-turn decision logic that evaluates (a) student's language choice, (b) current mastery, (c) scaffold tier, (d) whether language choice enables or undermines the pedagogical goal | Policy engine specification document |
| 1.4 | Define scaffold tiers formally: T1 (nudge/hint), T2 (conceptual explanation in student's terms), T3 (worked example with key steps), T4 (full solution) — each with language authorization rules | Scaffold tier taxonomy document |
| 1.5 | Define translanguaging-aware disclosure contracts: Language-specific authorization inspired by auditable release-control ideas (implemented independently) — a hint authorized in English may be unauthorized in Hindi depending on the LSM | Disclosure contract formal specification |
| 1.6 | Define Bayesian Knowledge Tracing (BKT) integration plan: How mastery estimates feed into scaffold tier selection and language policy decisions | BKT integration spec |

**Exit criteria:** All three translanguaging principles have formal computational mappings. LSM schema is defined and validated against 3 sample courses. Disclosure contracts are formally specified.

---

### Phase 2: Core Architecture — Agent Loop
**Duration:** Weeks 5–9
**Goal:** Build the agentic Perceive → Decide → Act → Reflect → Remember loop.

#### 2A: Perceive Module (Weeks 5–6)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2A.1 | Implement Language Detector: Per-turn language identification supporting English, Hindi, Bengali, Spanish, and code-mixed inputs (Hinglish, Benglish) | `perceive/language_detector.py` with >95% accuracy on test set |
| 2A.2 | Implement Mastery Tracker: BKT model estimating per-concept mastery from student responses (correct/incorrect/partial) | `perceive/mastery_tracker.py` with BKT state per session |
| 2A.3 | Implement Language Intent Classifier: Classify each language switch as legitimate translanguaging, adversarial switching, or neutral preference | `perceive/intent_classifier.py` |
| 2A.4 | Build the intent classifier training data: 500 legitimate + 500 adversarial + 500 neutral language-switch examples across 3 language pairs | `data/intent_classifier_dataset/` |
| 2A.5 | Implement Session State Manager: Maintain per-session history — turns, languages used, mastery estimates, scaffold tiers delivered, disclosed components | `perceive/session_state.py` |

**Intent Classifier approach:**
- Use a lightweight fine-tuned model (e.g., multilingual-e5 + classification head) or an LLM-as-judge approach with structured output.
- Features: mastery level, language switch pattern, semantic similarity of current question to previous questions (re-ask detection), scaffold tier history, timing.

#### 2B: Decide Module (Weeks 6–7)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2B.1 | Implement LSM Policy Engine: Load YAML LSM config; given (language, mastery, topic), return the maximum authorized scaffold tier | `decide/lsm_engine.py` |
| 2B.2 | Implement Scaffold Tier Selector: Given mastery estimate + LSM constraints + pedagogical goal, select the optimal scaffold tier for this turn | `decide/scaffold_selector.py` |
| 2B.3 | Implement Response Language Selector: Decide the response language — match student's language, use the LSM-authorized language, or fall back to English | `decide/language_selector.py` |
| 2B.4 | Implement Disclosure Contract Checker: Before generation, verify that the planned disclosure (tier + language) is authorized by the contract | `decide/disclosure_checker.py` |
| 2B.5 | Wire Perceive → Decide: Session state flows into decision module, producing a generation plan (scaffold tier, response language, disclosure authorization) | Integration test passing |

#### 2C: Act Module (Weeks 7–8)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2C.1 | Implement Constrained LLM Executor: Generate the tutoring response under constraints — system prompt encodes the authorized tier + language + disclosure limits | `act/llm_executor.py` |
| 2C.2 | Implement prompt templates for each scaffold tier × language combination | `act/prompt_templates/` |
| 2C.3 | Implement response rewriter: If the LLM over-discloses, rewrite the response to conform to the authorized tier (fallback mechanism) | `act/rewriter.py` |
| 2C.4 | Implement block/withhold action: When disclosure is unauthorized, generate an appropriate refusal that explains why (in the student's language) without being punitive | `act/refusal_generator.py` |

#### 2D: Reflect & Remember Module (Weeks 8–9)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2D.1 | Implement Multilingual Post-Check: After generation, verify the response for (a) cross-lingual leakage, (b) scaffold consistency, (c) cultural appropriateness | `reflect/post_checker.py` |
| 2D.2 | Implement cross-lingual leakage detector: Check if the response discloses in L2 what was withheld in L1, using multilingual embeddings + entailment | `reflect/leakage_detector.py` |
| 2D.3 | Implement scaffold consistency checker: Verify the delivered scaffold tier matches the authorized tier (catch LLM over-helpfulness) | `reflect/scaffold_checker.py` |
| 2D.4 | Implement escalation logic: When post-check fails, route to teacher queue with the full session trace, risk assessment, and recommended action | `reflect/escalation.py` |
| 2D.5 | Implement session memory update: After each turn, update session state with the delivered response, actual scaffold tier, actual disclosure, updated mastery, and post-check results | `remember/session_updater.py` |
| 2D.6 | Wire the full agent loop: Perceive → Decide → Act → Reflect → Remember → next turn | End-to-end agent loop integration test |

**Exit criteria:** Complete agent loop running via CLI/API. A student can converse in English, switch to Hindi, and the system correctly identifies the switch, selects the right scaffold tier, generates a response, post-checks it, and updates session state.

---

### Phase 3: Policy & Configuration Layer
**Duration:** Weeks 9–11
**Goal:** Build the teacher-facing policy layer and validate it with sample configurations.

| Task | Description | Deliverable |
|------|-------------|-------------|
| 3.1 | Define the full LSM YAML schema with JSON Schema validation | `configs/lsm_schema.json` + validator |
| 3.2 | Create LSM presets for 3 courses: (a) Intro to Python, (b) Linear Algebra, (c) General Science | 3 validated YAML configs |
| 3.3 | Implement LSM config loader with hot-reload support (teacher can update policy mid-course) | Config loader with validation + reload |
| 3.4 | Define the escalation policy schema: configurable thresholds for when to warn, rewrite, escalate, or block | Escalation policy YAML schema |
| 3.5 | Build a simple CLI tool for teachers to preview LSM behavior ("If a student asks X in language Y at mastery Z, what tier do they get?") | `tools/lsm_preview_cli.py` |
| 3.6 | Write documentation for teachers on how to configure LSM policies | `docs/teacher_guide.md` |

**Exit criteria:** 3 complete LSM configs validated. CLI preview tool working. A non-technical educator can understand the config format.

---

### Phase 3.5: Product UI (Student + Teacher)
**Duration:** Weeks 10–14 (overlaps Phase 3–4)
**Goal:** Ship a usable web UI for this independent project — student tutoring chat and teacher policy/escalation console — backed by the TL-Guard API.

This is **in scope** for the project (demo, usability study E5, and paper artifact), not deferred post-paper.

#### UI goals

| Audience | Primary jobs | Must show |
|----------|--------------|-----------|
| **Student** | Multilingual tutoring chat; switch languages freely | Detected language, scaffold tier used (optional transparency), clear refusals/escalations without punitive tone |
| **Teacher** | Configure LSM; review escalations; inspect session traces | LSM matrix editor, escalation queue, per-session risk/policy log |

#### Recommended stack

| Layer | Choice | Why |
|-------|--------|-----|
| API | FastAPI + WebSocket (or SSE) for chat streaming | Matches Python agent; easy OpenAPI for the UI |
| Student UI | Next.js (App Router) **or** Streamlit MVP first then Next.js | Streamlit for fast research demo; Next.js if polish / SUS study matters |
| Teacher UI | Same app, role-gated `/teacher` routes | One deployable product |
| Auth (lightweight) | Local roles: `student` / `teacher` (no SSO required for research prototype) | Enough for E5 and demos |

#### Tasks

| Task | Description | Deliverable |
|------|-------------|-------------|
| U1 | Expose agent loop as HTTP API: `POST /sessions`, `POST /sessions/{id}/turns`, `GET /sessions/{id}`, `GET /escalations` | OpenAPI-documented FastAPI service |
| U2 | Stream assistant replies (token or chunk streaming) so chat feels interactive | Streaming chat endpoint |
| U3 | **Student Chat UI:** message list, language indicator, optional “help level” badge (T1–T4), input that accepts Devanagari / Bangla / Latin scripts | Working student chat against live agent |
| U4 | Session side panel: mastery estimates (simple bars), languages used this session, policy outcome per turn (safe / rewrite / escalate / block) | Side panel wired to session state |
| U5 | **Teacher LSM Editor UI:** visual Language–Scaffold Matrix (languages × tiers allow/deny), YAML import/export, validate against schema | Teachers can edit LSM without writing YAML by hand |
| U6 | **Teacher Escalation Console:** queue of escalated turns, full trace, recommended action, resolve/dismiss | Escalation workflow usable in E5 |
| U7 | Demo mode: one-click load of sample Python/math courses + sample LSM presets | Demo script for supervisor / reviewers |
| U8 | Basic responsive layout (desktop-first; usable on tablet) + i18n-friendly fonts for Hindi/Bengali | UI checklist passed |
| U9 | Wire UI into E5 (teachers configure LSM via UI, not only CLI) | E5 protocol updated to use Teacher UI |

**Exit criteria:** Student can complete a 5-turn multilingual tutoring session in the UI. Teacher can edit an LSM, save it, and see it take effect on the next student turn. Escalations appear in the teacher console.

**UI out of scope for v1:** voice I/O, LMS SSO (Canvas/Moodle), mobile-native apps, multi-tenant cloud hosting.

---

### Phase 4: Multilingual Learner Personas & Data Generation
**Duration:** Weeks 11–14
**Goal:** Create the simulated evaluation dataset.

| Task | Description | Deliverable |
|------|-------------|-------------|
| 4.1 | Design 5 multilingual learner personas with distinct profiles | Persona specification document |
| 4.2 | Implement persona-driven student simulator: An LLM-based agent that plays the role of a multilingual student with specific mastery, language preferences, and translanguaging patterns | `simulation/student_simulator.py` |
| 4.3 | Generate simulated tutoring sessions: 5 personas × 3 language pairs × 4 conditions × 10 concepts × 5 turns = 3,000 sessions | `data/simulated_sessions/` |
| 4.4 | Annotate a stratified sample (20%) with human labels for: scaffold tier correctness, leakage (yes/no), translanguaging legitimacy, mastery trajectory | Annotated subset with inter-annotator agreement |
| 4.5 | Create adversarial language-switching scenarios: 500 sessions where the simulated student deliberately attempts to extract information via language switches | `data/adversarial_sessions/` |
| 4.6 | Create the intent classification evaluation set from annotated data | `data/intent_eval/` |

**Persona profiles (initial design):**

| Persona | L1 | L2 | Mastery | Translanguaging Pattern |
|---------|----|----|---------|------------------------|
| P1 | Hindi | English | Low | Frequently switches to Hindi for concept clarification |
| P2 | Bengali | English | Medium | Uses Bengali for vocabulary retrieval, English for code |
| P3 | Spanish | English | High | Minimal switching, occasionally uses Spanish for complex explanations |
| P4 | Hindi+English (bilingual) | — | Medium | Natural code-mixing (Hinglish), no clear L1/L2 |
| P5 | Bengali | English | Low | Switches aggressively — some legitimate, some adversarial |

**Four evaluation conditions:**
1. **C1: English-only** — Tutor responds only in English regardless of student language
2. **C2: Unguardrailed multilingual** — Tutor responds in any language, no scaffold controls
3. **C3: Content-safety guardrailed** — NeMo-style content safety applied, but no pedagogical awareness
4. **C4: TL-Guard** — Full architecture with LSM, intent classifier, disclosure contracts

**Exit criteria:** 3,000 simulated sessions generated. 600 human-annotated. Adversarial set created.

---

### Phase 5: Experiments & Evaluation
**Duration:** Weeks 14–19
**Goal:** Run all experiments, collect metrics, analyze results.

#### Experiment E1: LSM Policy Validation (Week 14)

| Detail | Value |
|--------|-------|
| **Question** | Does the LSM correctly enforce per-tier, per-language disclosure? |
| **Design** | 100 test scenarios × 3 languages × 5 tiers = 1,500 checks |
| **Metrics** | Policy compliance rate (target: >95%) |
| **Implementation** | Automated test suite against the LSM engine |

#### Experiment E2: Intent Classification (Weeks 14–15)

| Detail | Value |
|--------|-------|
| **Question** | Can TL-Guard distinguish legitimate translanguaging from adversarial switching? |
| **Design** | 500 legitimate + 500 adversarial + 500 neutral instances, 3-fold cross-validation |
| **Metrics** | Precision, Recall, F1 per class; macro-F1 |
| **Baselines** | (B1) Always-legitimate, (B2) Rule-based heuristic, (B3) Monolingual classifier |

#### Experiment E3: Comparative Tutoring (Weeks 15–17)

| Detail | Value |
|--------|-------|
| **Question** | Does TL-Guard improve learning outcomes vs. baselines? |
| **Design** | 5 personas × 3 language pairs × 4 conditions × 10 concepts × 5 turns |
| **Metrics** | Mastery gain (BKT Δ), leakage rate, scaffold integrity, translanguaging support quality |
| **Statistical tests** | Paired t-tests / Wilcoxon signed-rank across conditions with Bonferroni correction |

#### Experiment E4: False Suppression Analysis (Week 17)

| Detail | Value |
|--------|-------|
| **Question** | How often does TL-Guard incorrectly block legitimate translanguaging? |
| **Design** | Human-annotated subset of E3 (all TL-Guard sessions with a language switch) |
| **Metrics** | False positive rate on legitimate translanguaging (target: <10%) |

#### Experiment E5: Teacher Usability (Week 18)

| Detail | Value |
|--------|-------|
| **Question** | Can teachers understand and configure the LSM? |
| **Design** | 5 multilingual educators configure LSM for their own course |
| **Metrics** | Task completion rate, time-on-task, System Usability Scale (SUS) score |
| **Note** | Requires recruiting 5 educators; may run in parallel with E3/E4. Teachers configure LSM via the **Teacher UI** (Phase 3.5), not only YAML/CLI. |

#### Analysis & Ablations (Weeks 18–19)

| Task | Description |
|------|-------------|
| Ablation: Remove intent classifier | Measure impact on false suppression and leakage rates |
| Ablation: Remove post-check | Measure impact on scaffold integrity |
| Ablation: Fixed policy vs. adaptive | Compare static LSM with mastery-adaptive tier selection |
| Error analysis | Categorize failure modes: false suppressions, missed leakage, cultural errors |
| Cross-model comparison | Run E3 with GPT-4o, LLaMA 3.1, and Qwen 2.5 — confirm model-agnostic behavior |

**Exit criteria:** All 5 experiments complete. Results tables and figures generated. Ablation analysis done. Error taxonomy created.

---

### Phase 6: Paper Writing & Submission
**Duration:** Weeks 19–24
**Goal:** Write, revise, and submit the paper.

| Task | Duration | Deliverable |
|------|----------|-------------|
| 6.1 Draft Introduction + Related Work | Week 19 | Sections 1–2 (3.5 pages) |
| 6.2 Draft Operationalizing Translanguaging | Week 20 | Section 3 (2 pages) |
| 6.3 Draft TL-Guard Architecture | Week 20 | Section 4 (2.5 pages) |
| 6.4 Draft Experimental Design + Results | Week 21 | Sections 5–6 (3.5 pages) |
| 6.5 Draft Discussion + Conclusion | Week 21 | Sections 7–8 (2 pages) |
| 6.6 Internal review round 1 | Week 22 | Supervisor feedback |
| 6.7 Revision + figures/tables polish | Week 22–23 | Camera-ready draft |
| 6.8 Internal review round 2 | Week 23 | Final feedback |
| 6.9 Final revision + submission | Week 24 | Submitted paper |

**Paper structure (14 pages target):**

1. Introduction (1.5 pp)
2. Theoretical Background (2 pp)
3. Operationalizing Translanguaging for AI Agents (2 pp)
4. TL-Guard Architecture (2.5 pp)
5. Experimental Design (1.5 pp)
6. Results (2 pp)
7. Discussion (1.5 pp)
8. Conclusion and Future Work (0.5 pp)
9. References
10. Appendices

**Target venues (ranked by fit):**
1. *International Journal of Artificial Intelligence in Education* (Springer) — best fit for AI + pedagogy
2. *Computers & Education* (Elsevier) — high impact, broad audience
3. *Technology, Knowledge and Learning* (Springer) — where KiKo-Prim was published
4. *British Journal of Educational Technology* (Wiley)

---

## 4. Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Language | Python 3.11+ | Ecosystem support for NLP/ML |
| Agent | **TLGuardAgent** (Perceive → Decide → Act → Reflect → Remember) | Independent project — no EduHarness dependency |
| API | FastAPI | Serves agent to UI and experiments |
| Student + Teacher UI | Streamlit (MVP) **or** Next.js + React | Research demo vs. polished SUS study |
| LLM inference (cloud) | OpenAI API (GPT-4o) | State-of-the-art multilingual capability |
| LLM inference (local) | vLLM / Ollama | LLaMA 3.1 8B, Qwen 2.5 7B local serving |
| Language detection | fastText lid.176.bin + lingua-py | Best coverage for Indian languages + code-mixed text |
| Multilingual embeddings | multilingual-e5-large (Hugging Face) | Shared embedding space for cross-lingual leakage detection |
| Knowledge tracing | pyBKT or custom BKT | Bayesian Knowledge Tracing for mastery estimation |
| Policy engine | YAML + pydantic | Type-safe LSM config loading and validation |
| Experiment tracking | Weights & Biases | Experiment logging, comparison, reproducibility |
| Testing | pytest + hypothesis | Unit tests + property-based testing for policy compliance |
| Data annotation | Label Studio | Human annotation of simulated sessions |

---

## 5. Directory Structure

```
tl-guard/                         # Independent repo (this project)
├── src/
│   ├── pipeline/                 # Act + Reflect executor (execute_act_reflect)
│   │   ├── verify.py
│   │   ├── executor.py
│   │   ├── post_check.py
│   │   └── turn_pipeline.py
│   ├── perceive/
│   │   ├── language_detector.py
│   │   ├── mastery_tracker.py
│   │   ├── intent_classifier.py
│   │   └── session_state.py
│   ├── decide/
│   │   ├── lsm_engine.py
│   │   ├── scaffold_selector.py
│   │   ├── language_selector.py
│   │   └── disclosure_checker.py
│   ├── act/
│   │   ├── llm_executor.py
│   │   ├── rewriter.py
│   │   ├── refusal_generator.py
│   │   └── prompt_templates/
│   ├── reflect/
│   │   ├── post_checker.py
│   │   ├── leakage_detector.py
│   │   ├── scaffold_checker.py
│   │   └── escalation.py
│   ├── remember/
│   │   └── session_updater.py
│   ├── agent.py                  # Main agent loop orchestrator
│   └── config_loader.py
├── api/
│   ├── main.py                   # FastAPI app
│   ├── routes/
│   │   ├── sessions.py
│   │   ├── turns.py
│   │   ├── policies.py
│   │   └── escalations.py
│   └── schemas.py
├── ui/                           # Student + Teacher product UI
│   ├── student/                  # Chat tutoring interface
│   ├── teacher/                  # LSM editor + escalation console
│   └── README.md                 # How to run UI against local API
├── configs/
│   ├── lsm_schema.json
│   ├── lsm_python_intro.yaml
│   ├── lsm_linear_algebra.yaml
│   ├── lsm_general_science.yaml
│   └── escalation_policy.yaml
├── simulation/
│   ├── student_simulator.py
│   └── personas/
├── data/
│   ├── simulated_sessions/
│   ├── adversarial_sessions/
│   ├── intent_classifier_dataset/
│   └── intent_eval/
├── experiments/
│   ├── e1_lsm_validation.py
│   ├── e2_intent_classification.py
│   ├── e3_comparative_tutoring.py
│   ├── e4_false_suppression.py
│   └── e5_teacher_usability.py
├── tests/
├── notebooks/
│   ├── analysis.ipynb
│   └── figures.ipynb
├── docs/
│   ├── teacher_guide.md
│   └── reading_notes/
├── tools/
│   └── lsm_preview_cli.py
├── pyproject.toml
└── README.md
```

---

## 6. Key Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Language detection fails on code-mixed text (Hinglish/Benglish) | High — cascading errors in intent classification and LSM lookup | Medium | Ensemble fastText + lingua-py; train on code-mixed corpora; fall back to "mixed" label with conservative policy |
| LLM over-discloses despite constrained prompts | High — scaffold integrity violation | High | Response rewriter as safety net; post-check catches remaining leaks; constrained decoding where possible |
| Intent classifier cannot reliably distinguish legitimate vs. adversarial switching | High — either false suppressions (bad UX) or missed attacks (unsafe) | Medium | Conservative default (allow with logging); use mastery context as strong signal; human-in-the-loop escalation |
| BKT mastery estimates are noisy with few interactions | Medium — scaffold tier selection may be suboptimal | Medium | Prior calibration from curriculum difficulty; minimum 3 interactions before mastery influences tier; teacher override option |
| Multilingual embeddings have lower quality for Bengali | Medium — leakage detector less effective for En-Bn pair | Medium | Evaluate embedding quality per language pair; use language-specific thresholds; supplement with translation-based checks |
| Simulated personas don't represent real students | Medium — ecological validity concern | High | Acknowledge as limitation; design for future IRB-approved human study; validate persona behaviors with educators |
| Teacher usability study: small sample (n=5) | Low — limited generalizability of usability findings | Medium | Treat as formative evaluation, not summative; triangulate with think-aloud protocols |
| UI delayed behind agent work | Medium — blocks E5 and demos | Medium | Start API stubs early (P0); ship Streamlit MVP first if Next.js slips; E5 can fall back to CLI only as last resort |

---

## 7. Milestones & Timeline Overview

```
Week  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
      ├──┤  ├─────┤  ├─────────────┤  ├─────┤  ├──────────────────┤  ├──────────┤
      P0     P1          P2             P3          P4                   P5
      Setup  Theory      Core Arch.     Policy      Data Gen.            Eval
                              └────────── P3.5 UI (API + Student + Teacher) ──┘
                                                                    ├──────────────┤
                                                                         P6: Paper

M1 ──────┤ Independent env + stub pipeline + UI/API scaffold (end Week 2)
M2 ──────────────┤ Theory formalized, LSM schema defined (end Week 5)
M3 ──────────────────────────────┤ Agent loop end-to-end working (end Week 9)
M4 ──────────────────────────────────────┤ Policy layer complete (end Week 11)
M4b ────────────────────────────────────────────────┤ Student + Teacher UI usable (end Week 14)
M5 ──────────────────────────────────────────────────┤ Dataset generated (end Week 14)
M6 ──────────────────────────────────────────────────────────────────┤ All experiments done (end Week 19)
M7 ──────────────────────────────────────────────────────────────────────────────────┤ Paper submitted (end Week 24)
```

---

## 8. Evaluation Metrics Summary

| Metric | Definition | Target | Experiment |
|--------|-----------|--------|------------|
| Policy compliance rate | % of turns where the delivered scaffold tier matches LSM authorization | >95% | E1 |
| Intent classification F1 | Macro-F1 across legitimate/adversarial/neutral | >0.80 | E2 |
| Mastery gain (Δ BKT) | Change in BKT mastery estimate pre→post interaction | Higher than C1 baseline | E3 |
| Leakage rate | % of turns where the tutor discloses beyond the authorized tier | <5% | E3 |
| Scaffold integrity | % of sessions where scaffold tier never exceeds authorized level | >90% | E3 |
| Translanguaging support quality | % of legitimate translanguaging instances correctly permitted | >90% | E3, E4 |
| False suppression rate | % of legitimate translanguaging incorrectly blocked | <10% | E4 |
| SUS score | System Usability Scale for LSM configuration | >68 (above average) | E5 |

---

## 9. Dependencies & Prerequisites

| Dependency | Status | Action Needed |
|------------|--------|---------------|
| EduHarness | **Not used** | Independent agentic system — LLM is a tool inside Act |
| OpenAI API access (GPT-4o) | Required | API key with sufficient quota for ~3,000+ sessions |
| GPU for local LLM inference | Required | LLaMA 3.1 8B and Qwen 2.5 7B need ≥24 GB VRAM (A100/4090) |
| fastText language ID model | Available | Download lid.176.bin |
| multilingual-e5-large | Available | Download from Hugging Face |
| Node.js (if Next.js UI) | Optional | Only if choosing Next.js over Streamlit MVP |
| Label Studio instance | Optional | For annotation workflow; can substitute spreadsheet-based annotation |
| 5 multilingual educators (E5) | Required for E5 | Recruit from IIEST / partner institutions; use Teacher UI for LSM tasks |
| Supervisor approval | Required | Review this plan before Phase 1 begins |

---

## 10. Definition of Done

The project is complete when:

1. TL-Guard agent loop runs end-to-end across all 3 language pairs **as an independent system** (no EduHarness dependency)
2. Agent Act + Reflect (`authorize → LLM tool → post-check`) is the sole generation path
3. LSM policy engine correctly enforces >95% of tier-language combinations
4. Intent classifier achieves >0.80 macro-F1 on the evaluation set
5. Comparative evaluation (E3) shows measurable improvement over at least 2 of 3 baselines on at least 2 metrics
6. False suppression rate is <10%
7. **Student Chat UI** supports a full multilingual tutoring session; **Teacher UI** supports LSM edit + escalation review
8. Paper is submitted to a target venue
9. Code and (non-proprietary) data are packaged for reproducibility

---

## 11. Future Work (Post-Paper)

These are explicitly out of scope for this paper but planned for subsequent work:

- Real classroom deployment with IRB-approved human subjects study
- Voice-based translanguaging buddy (speech → text → TL-Guard → text → speech)
- Extension to additional language pairs (Tamil, Telugu, Mandarin)
- Optional research integration with XL-CRA-style risk signals (separate project; not a code dependency)
- Adaptive LSM policies that learn from teacher corrections over time
- LMS SSO, multi-tenant hosting, and production hardening of the UI
