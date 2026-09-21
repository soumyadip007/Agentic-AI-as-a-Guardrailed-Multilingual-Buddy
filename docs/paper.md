# Agentic AI as a Guardrailed Multilingual Buddy: Translanguaging Support Under Pedagogical Safety Constraints

Soumyadip Chowdhury^{1}  
^{1}Indian Institute of Engineering Science and Technology, Shibpur, India

---

**Abstract.** In multilingual educational settings, students routinely mix languages while learning—a practice known as translanguaging. Contemporary AI tutoring systems either restrict interaction to a single language or permit unconstrained multilingual dialogue that undermines pedagogical safety through answer leakage and scaffolding collapse. In this paper, we propose **TL-Guard**, an agentic AI tutoring framework that supports legitimate translanguaging while enforcing teacher-defined pedagogical safety constraints. Unlike chatbot-style multilingual buddies that map each utterance to an unconstrained LLM completion, TL-Guard is a goal-driven agent with a closed decision loop: **Perceive → Decide → Act → Reflect → Remember**. The large language model (LLM) is used only as a tool inside Act. Central to the framework is the **Language–Scaffold Matrix (LSM)**, a teacher-configurable policy matrix $M \in \{0,1\}^{|L|\times 4}$ that authorizes scaffold tiers (hint, explanation, worked example, full solution) per language. A **Language Intent Classifier** distinguishes legitimate clarification from adversarial answer-seeking using mastery context and interaction history, while **translanguaging-aware disclosure contracts** prevent cross-lingual leakage. We implement TL-Guard in Python with a local Ollama LLM backend, FastAPI, and dual-role Streamlit interfaces. Preliminary evaluation across three language pairs (English–Hindi, English–Bengali, English–Spanish) yields 100% LSM policy compliance over 60 matrix cells, with end-to-end unit tests confirming correct agent behaviour on legitimate and adversarial translanguaging trajectories.

**Keywords:** Translanguaging · Agentic AI · Pedagogical Safety · Multilingual Tutoring · Language–Scaffold Matrix · Guardrails · Scaffolding

---

## 1 Introduction

A university or school tutoring system consists of several functional modules; among the most important is formative, interactive support for concept understanding. In multilingual regions of India and the Global South, this support is rarely monolingual. A student studying introductory programming may ask a question in English, seek clarification in Hindi or Bengali, write pseudocode in a code-mixed register (e.g., Hinglish), and return to English for final code [1–3]. García and Li Wei [3] term this fluid use of the full linguistic repertoire **translanguaging**. Empirical evidence indicates that translanguaging is not a deficit but a productive learning strategy that aids concept formation, vocabulary retrieval, and metacognitive reflection [1, 4, 5].

Despite the pedagogical value of translanguaging, digital tutoring systems create a design tension. On one hand, **safety-focused AI tutors** [10–12] attempt to prevent pedagogical harm—answer leakage, scaffolding collapse, and over-disclosure—yet typically operate in English and may treat language switching as an attack vector [13, 14]. On the other hand, **multilingual buddy systems** [6–9, 15] welcome language mixing but lack formal control over *how much* help is delivered *in which* language. Consequently, a student may be denied a full solution in English and later obtain it by restating the request in Hindi—a failure mode known as **cross-lingual leakage** [16].

Formally, let a tutoring session be a sequence of turns $S = \{(u_t, a_t, \ell_t, \tau_t)\}_{t=1}^{T}$, where $u_t$ is the student utterance, $a_t$ the agent response, $\ell_t$ the detected language, and $\tau_t$ the scaffold tier. Pedagogical safety requires that the disclosure of solution-bearing content be consistent with a teacher policy $\Pi$. Cross-lingual leakage occurs when

$$
\exists\, t < t',\quad \text{Withheld}(a_t,\tau_t) \land \text{Disclosed}(a_{t'},\tau_{t'}) \land \ell_t \neq \ell_{t'},
\tag{1}
$$

i.e., content withheld under policy in one language is later disclosed after a language switch.

Keeping this requirement in mind, in this paper we propose **TL-Guard** (TransLanguaging-Aware Guardrailed AI Buddy): an editable, teacher-configurable, agentic framework for multilingual tutoring that (i) operationalizes García et al.’s Stance/Design/Shifts [1] computationally, (ii) authorizes help via an LSM policy matrix, (iii) classifies switch intent, and (iv) self-audits LLM drafts before student delivery. TL-Guard is an **agent**, not a chatbot wrapper: safety is native to Decide/Act/Reflect, and the LLM is invoked only inside Act.

The contributions of this work are:

- **C1.** Computational operationalization of Stance / Design / Shifts for AI tutoring agents.
- **C2.** The Language–Scaffold Matrix (LSM) $M$ as a formal teacher policy artifact.
- **C3.** Translanguaging-aware disclosure contracts with cross-lingual consistency (Eq. 1 mitigation).
- **C4.** A Language Intent Classifier combining mastery, re-ask overlap, and multilingual cues.
- **C5.** A complete open-source implementation with Ollama, FastAPI, Streamlit, and Docker deployment.

The rest of this paper is organized as follows. Section 2 summarizes a review of existing literature on multilingual AI buddies, translanguaging pedagogy, and pedagogical safety. Section 3 describes the proposed methodology. Section 4 elucidates the practical implementation of the proposed methodology. The paper concludes in Section 5 with directions toward future research.

---

## 2 Literature Review

There has been substantial research on AI tutoring, multilingual education technology, and pedagogical guardrails. We organize the review into five streams and identify the intersectional gap that TL-Guard addresses.

### 2.1 Chatbots versus Agents in Educational AI

Most commercial and research “learning buddies” are **chatbots**: a function $f:(u_t) \mapsto a_t$ that maps the current utterance to an LLM completion, optionally with retrieval. An **agent**, by contrast, maintains state $s_t$ and executes a closed loop

$$
s_{t+1} = \mathcal{R}\big(\mathcal{A}\big(\mathcal{D}\big(\mathcal{P}(u_t,s_t)\big)\big)\big),
\tag{2}
$$

where $\mathcal{P}$, $\mathcal{D}$, $\mathcal{A}$, and $\mathcal{R}$ denote Perceive, Decide, Act, and Reflect (with Remember updating $s_{t+1}$). Equation (2) makes explicit that generation is subordinated to deliberation. KiKo-Prim [6] and GurukulAI [8] are chatbot-style; TL-Guard instantiates Eq. (2).

### 2.2 AI as a Multilingual Buddy

KiKo-Prim [6] coined “multilingual buddy” through analysis of 462 conversational turns in Grades 3–4 classrooms, showing ChatGPT support for vocabulary retrieval and multilingual artifact production. Productive use depended on guided prompting and teacher facilitation. Walter [7] reported statistically significant oral-presentation gains ($p<.001$, Cohen’s $d=0.75$) using sociocultural theory (More Knowledgeable Other within the Zone of Proximal Development), but the system is English-only. Acharjo [9] built curriculum-aligned tutoring for Bengali and Assamese with GPT-3.5 and RAG (22% pedagogical accuracy improvement). GurukulAI [8] aligned LLaMA 3.1 8B to NCERT Hindi–English content. 7S Samiti [15] deployed voice-first Hindi–English tutoring for rural India. Across these systems, **no formal per-language scaffold policy** and **no agentic safety loop** are reported.

### 2.3 Translanguaging Theory and Pedagogy

García, Johnson, and Seltzer [1] define three pedagogical principles: **Stance** (multilingualism as resource), **Design** (purposeful planning of multilingual instruction), and **Shifts** (moment-to-moment instructional adjustment). García and Li Wei [3] argue that bilingual speakers deploy a single integrated repertoire rather than two separate language systems—implying that AI tutors should not enforce hard language separation. Cummins’ Linguistic Interdependence Hypothesis [4, 5] states that academic proficiency transfers across languages, providing theoretical justification for cross-lingual concept building. STEM meta-syntheses [18] document gaps in computer science and mathematics and persistent monoglossic ideologies in educational technology. These frameworks are established for *human* teachers; computational operationalization for AI agents remains scarce.

### 2.4 Pedagogical Safety in AI Tutoring

SafeTutors [10] showed that pedagogical harm rises from 17.7% in single-turn to 77.8% in multi-turn tutoring. SHAPE [11] proposed graph-augmented mastery-aware routing. Auditable Release Control [17] formalized disclosure contracts with deterministic and semantic verification. Simulations of multilingual math tutoring [16] found higher leakage rates in low-resource languages. Collectively, these works establish that **scaffolding integrity is fragile** and that multilingual settings amplify risk—yet their implementations remain largely English-centric.

### 2.5 Guardrail Systems for Multilingual Education

NeMo Guardrails [12] provides YAML-programmable rails and multilingual refusal messages, but without scaffold-tier pedagogical semantics. EvalGuard [19] offers policy-as-code for educational agents with privacy compliance, English-only. CSRT [14] and MultiJail [13] show that code-switching and low-resource languages increase jailbreak success. Indian Multilingual Prompt Injection work [20] achieves 99.70% detection accuracy on Hindi/Hinglish attacks. These systems treat language mixing primarily as a security threat rather than a learning resource.

### 2.6 Research Gap

**Table 1.** Gap analysis at the intersection of four research streams.

| Stream | Existing Work | Missing Capability |
|---|---|---|
| Multilingual buddy | [6–9, 15] | Pedagogical safety under language mixing |
| Translanguaging theory | [1–5, 18] | Computational agent operationalization |
| Pedagogical safety | [10, 11, 16, 17] | Multilingual disclosure control |
| Guardrails | [12–14, 19, 20] | Scaffold integrity *while supporting* translanguaging |

**Gap statement.** No existing system integrates García’s Stance/Design/Shifts into an AI tutoring *agent* with formal, teacher-configurable, language-aware pedagogical safety constraints that distinguish legitimate translanguaging from adversarial switching.

---

## 3 Proposed Methodology

In this section, we elaborate the proposed TL-Guard framework. Stakeholders operate at two levels: the **teacher (policy) level** and the **student (interaction) level**. Teachers configure the LSM and review escalations; students interact in any supported language. The LLM is never a free-standing chatbot—it is invoked only after Decide authorizes a generation plan.

### 3.1 Preliminaries and Notation

Let $L = \{\mathrm{en},\mathrm{hi},\mathrm{bn},\mathrm{es},\mathrm{mixed}\}$ be the set of supported languages (and code-mixed class). Let the ordered scaffold set be

$$
\mathcal{T} = \{T_1,T_2,T_3,T_4\}, \qquad
\mathrm{rank}(T_1)<\mathrm{rank}(T_2)<\mathrm{rank}(T_3)<\mathrm{rank}(T_4),
\tag{3}
$$

where $T_1$ = nudge/hint, $T_2$ = conceptual explanation, $T_3$ = worked example, $T_4$ = full solution.

**Definition 1 (Language–Scaffold Matrix).** An LSM for a course is a Boolean matrix $M \in \{0,1\}^{|L|\times 4}$ together with escalation policy $\mathcal{E}$. Entry $M_{\ell,\tau}=1$ iff tier $\tau$ is authorized in language $\ell$.

**Definition 2 (Authorization).** Pair $(\ell,\tau)$ is authorized iff $M_{\ell,\tau}=1$.

**Definition 3 (Tier Clamping).** For desired tier $\tau_d$ and language $\ell$,

$$
\tau_a(\ell,\tau_d) = \arg\max_{\tau \in \mathcal{T}} \big\{\mathrm{rank}(\tau) \;\big|\; \mathrm{rank}(\tau)\le \mathrm{rank}(\tau_d) \land M_{\ell,\tau}=1\big\}.
\tag{4}
$$

If no such $\tau$ exists, generation is unauthorized and Act refuses without calling the LLM.

**Definition 4 (Session State).** Session state at turn $t$ is

$$
s_t = \big(H_t,\; p_t,\; \mathcal{L}_t,\; \tau^{\mathrm{last}}_t,\; r_t,\; w_t\big),
\tag{5}
$$

where $H_t$ is turn history, $p_t\in(0,1)$ is BKT mastery, $\mathcal{L}_t\subseteq L$ is the set of languages used, $\tau^{\mathrm{last}}_t$ is the last authorized tier, $r_t$ is the consecutive-rewrite counter, and $w_t\in\{0,1\}$ indicates whether prior turns withheld content in another language.

### 3.2 Theoretical Operationalization of Translanguaging

**Table 2.** Mapping García et al. [1] to TL-Guard constructs.

| Principle | Teacher behaviour | Computational construct |
|---|---|---|
| Stance | Welcome all languages | Affirmative system prompt; $\ell$-switches logged as features in $\mathcal{L}_t$ |
| Design | Plan multilingual instruction | LSM $M$ (Definition 1) per course |
| Shifts | Moment-to-moment adjustment | Decide: $(p_t,i_t,M)\mapsto(\tau_a,\ell_r)$ each turn |

Stance is encoded in the Act system prompt $\Sigma(\tau,\ell,c,k)$ for course $c$ and concept $k$:

$$
\Sigma(\tau,\ell,c,k) = \Sigma_{\mathrm{stance}} \,\Vert\, \Sigma_{\mathrm{tier}}(\tau) \,\Vert\, \Sigma_{\mathrm{lang}}(\ell) \,\Vert\, \Sigma_{\mathrm{ctx}}(c,k).
\tag{6}
$$

### 3.3 Agent Architecture

Figure 1 depicts the system and control perspectives of TL-Guard.

**Fig. 1.** TL-Guard agent architecture (system view).

```
┌─────────────────────────────────────────────────────────────┐
│                     TLGuardAgent (s_t)                      │
│  Student u_t ──► Perceive ──► Decide ──► Act ──► Reflect   │
│                      │          │         │         │       │
│                   lang,p,i    plan τ,ℓ   LLM tool  λ,out   │
│                      └──────────┴─────────┴─────────┘       │
│                                   │                         │
│                              Remember → s_{t+1}             │
│                                   │                         │
│                         Teacher Escalation Queue            │
└─────────────────────────────────────────────────────────────┘
```

#### 3.3.1 Perceive

**Language detection.** Let $\phi(u)$ extract Unicode script indicators and token cue scores. The detector returns

$$
(\ell_t, \gamma_t, m_t) = \mathcal{P}_{\mathrm{lang}}(u_t),
\tag{7}
$$

with confidence $\gamma_t\in[0,1]$ and code-mix flag $m_t\in\{0,1\}$. Pure Devanagari maps to $\mathrm{hi}$, pure Bengali script to $\mathrm{bn}$; simultaneous native+Latin scripts yield $\mathrm{mixed}$.

**Mastery estimation (BKT).** Following Corbett and Anderson [21], let $p_t = P(L_t=1)$ be the probability the concept is known. Given observation $o_t\in\{0,1,\emptyset\}$ (incorrect, correct, or no evidence),

$$
P(L_t\mid o_t{=}1) = \frac{p_t(1-p_S)}{p_t(1-p_S)+(1-p_t)p_G},
\tag{8}
$$

$$
P(L_t\mid o_t{=}0) = \frac{p_t\,p_S}{p_t\,p_S+(1-p_t)(1-p_G)},
\tag{9}
$$

$$
p_{t+1} = P(L_t\mid o_t) + \big(1-P(L_t\mid o_t)\big)\,p_T,
\tag{10}
$$

with parameters $(p_0,p_T,p_G,p_S)=(0.30,0.15,0.20,0.10)$ and clamp $p_{t+1}\in[0.01,0.99]$. If $o_t=\emptyset$ (clarification question), $p_{t+1}=p_t$.

**Intent classification.** When $\ell_t\neq\ell_{t-1}$ (or answer-seeking occurs without a switch), define adversarial and legitimate scores

$$
s_a = \alpha_1\mathbb{I}_{\mathrm{ans}}(u_t)+\alpha_2\mathbb{I}_{\mathrm{reask}}(u_t,H_t)+\alpha_3\mathbb{I}_{\mathrm{tier\uparrow}}(u_t,\tau^{\mathrm{last}}_t),
\tag{11}
$$

$$
s_\ell = \beta_1\mathbb{I}_{\mathrm{clar}}(u_t)+\beta_2\mathbb{I}_{p_t<0.35}\mathbb{I}_{\mathrm{clar}}(u_t)+\beta_3\mathbb{I}_{\ell_t\in L\setminus\{\mathrm{en}\}}\big(1-\mathbb{I}_{\mathrm{ans}}(u_t)\big),
\tag{12}
$$

with $(\alpha_1,\alpha_2,\alpha_3)=(0.45,0.35,0.20)$ and $(\beta_1,\beta_2,\beta_3)=(0.35,0.50,0.20)$. Re-ask uses Jaccard overlap of token sets:

$$
J(u,u') = \frac{|T(u)\cap T(u')|}{|T(u)\cup T(u')|},\qquad \mathbb{I}_{\mathrm{reask}}=\mathbf{1}[J\ge 0.55].
\tag{13}
$$

Intent is

$$
i_t =
\begin{cases}
\mathrm{adversarial}, & s_a\ge 0.55 \land s_a > s_\ell,\\
\mathrm{legitimate}, & s_\ell\ge 0.40,\\
\mathrm{neutral}, & \text{otherwise (on switch)},\\
\mathrm{none}, & \text{no switch and not adversarial}.
\end{cases}
\tag{14}
$$

#### 3.3.2 Decide

Desired tier from mastery:

$$
\tau_d(p_t) =
\begin{cases}
T_3, & p_t < 0.35,\\
T_2, & 0.35 \le p_t < 0.60,\\
T_1, & p_t \ge 0.60.
\end{cases}
\tag{15}
$$

If $i_t=\mathrm{adversarial}$ and $\mathcal{E}.\mathrm{on\_adversarial}=\mathrm{tighten}$, force $\tau_d\leftarrow T_1$. Then $\tau_a=\tau_a(\ell_t,\tau_d)$ by Eq. (4). Response language $\ell_r=\ell_t$ if $M_{\ell_t,\tau_a}=1$, else default $\ell_0$ (typically $\mathrm{en}$).

**Definition 5 (Generation Plan).**

$$
\pi_t = (\tau_a,\ell_r,\mathrm{auth}_t,i_t,\mathrm{tighten}_t),\qquad
\mathrm{auth}_t = \mathbf{1}[M_{\ell_r,\tau_a}=1].
\tag{16}
$$

**Definition 6 (Disclosure Contract).** Contract $\delta_t=(\ell_r,\tau_a,s_t)$ holds iff $\mathrm{auth}_t=1$, mastery policy approves $\tau_a$, and

$$
\neg\big(w_t=1 \land \mathrm{LooksFull}(a_{\mathrm{draft}})\big)
\tag{17}
$$

is enforced at Reflect (heightened leakage when $w_t=1$).

#### 3.3.3 Act

If $\mathrm{auth}_t=0$, return a non-punitive refusal $\rho(\ell_r)$ with no LLM call. Otherwise,

$$
a^{\mathrm{raw}}_t = \mathrm{LLM}\big(\Sigma(\tau_a,\ell_r,c,k),\; u_t\big),
\tag{18}
$$

with temperature $\theta=0.4$ (Ollama `/api/chat` by default).

#### 3.3.4 Reflect

Leakage score:

$$
\lambda(a,\tau_a,w_t) = \min\Big(1,\;
0.6\,\mathbb{I}_{\mathrm{full}}(a)\,\mathbb{I}_{\mathrm{rank}(\tau_a)<\mathrm{rank}(T_4)}
+ 0.3\,\mathbb{I}_{\mathrm{full}}(a)\,\mathbb{I}_{\tau_a\in\{T_1,T_2\}}
+ 0.4\,\mathbb{I}_{\mathrm{full}}(a)\,w_t
+ 0.2\,\mathbb{I}_{N_{\mathrm{code}}(a)\ge 3}\Big),
\tag{19}
$$

where $\mathbb{I}_{\mathrm{full}}$ detects solution-like dumps and $N_{\mathrm{code}}$ counts code keywords. Over-disclosure Boolean $od(a,\tau_a)$ flags tier inconsistency. Outcome:

$$
\omega_t =
\begin{cases}
\mathrm{SAFE}, & \lambda<0.5 \land \neg od,\\
\mathrm{REWRITE}, & \text{violation}\land \mathcal{E}.\mathrm{on\_leakage}=\mathrm{rewrite},\\
\mathrm{ESCALATE}, & \text{violation}\land \mathcal{E}.\mathrm{on\_leakage}=\mathrm{escalate},\\
\mathrm{BLOCK}, & \text{violation}\land \mathcal{E}.\mathrm{on\_leakage}=\mathrm{block}.
\end{cases}
\tag{20}
$$

On REWRITE/ESCALATE, $a_t=\mathrm{Rewrite}(a^{\mathrm{raw}}_t,\tau_a,\ell_r)$ (or $T_1$ under escalate). Escalation items are queued if $i_t=\mathrm{adversarial}$ under escalate policy, or if $r_t\ge 2$ consecutive rewrites:

$$
r_{t+1} =
\begin{cases}
r_t+1, & \omega_t=\mathrm{REWRITE},\\
0, & \text{otherwise}.
\end{cases}
\tag{21}
$$

#### 3.3.5 Remember

$$
s_{t+1} = \mathrm{Update}(s_t, \mathrm{TurnRecord}_t),
\tag{22}
$$

appending history and updating $\mathcal{L}_t$, $p_t$, $\tau^{\mathrm{last}}_t$, $r_t$, $w_t$.

### 3.4 Evaluation Methodology

We follow Design Science Research / FEDS [22]. Let policy compliance for cell $(\ell,\tau)$ be $C_{\ell,\tau}=\mathbf{1}[\mathrm{Engine}(\ell,\tau)=M_{\ell,\tau}]$. Aggregate compliance:

$$
C = \frac{1}{|L|\,|\mathcal{T}|}\sum_{\ell\in L}\sum_{\tau\in\mathcal{T}} C_{\ell,\tau}.
\tag{23}
$$

For intent classification (planned), precision/recall/F1 on balanced labels. For comparative tutoring (planned), mastery gain $\Delta p = p_T-p_0$, leakage rate, and scaffold integrity across four conditions. False-suppression rate measures incorrect blocking of legitimate L2 use.

---

## 4 Practical Implementation

In this section, we describe the practical implementation of TL-Guard. In particular, we describe the implementation setup, execution procedure, sample execution scenarios, and performance evaluation metrics.

### 4.1 Implementation Setup

The software platform is Python 3.11+ with Pydantic v2 models. The rationale for a local Ollama LLM backend is data locality, zero API cost for research demos, and reproducibility without cloud keys. Optional OpenAI is supported when `TL_GUARD_LLM=openai`.

**Hardware (minimum).** A computer system with a modern multi-core CPU, $\ge 8$ GB RAM ($\ge 16$ GB recommended for `llama3`), and persistent storage for model weights meets the requirements for running Ollama and the agent services.

**Software stack.**

**Table 3.** Implementation stack.

| Component | Technology | Role |
|---|---|---|
| Agent core | Python, Pydantic | `TLGuardAgent`, typed plans/turns |
| Act LLM tool | Ollama (`llama3` default) | Constrained generation (Eq. 18) |
| Mastery | BKT (Eqs. 8–10) | Perceive input |
| API | FastAPI + Uvicorn | Session/turn/policy HTTP API |
| UI | Streamlit | Student Buddy + Teacher Console |
| CLI | Typer (`tl-guard`) | doctor, demo, chat, preview |
| Config | YAML LSM | Teacher policy $M$, $\mathcal{E}$ |
| Docs | MkDocs Material | Workflow + paper |
| Deploy | Docker Compose | API :8000, UI :8501, Docs :8001 |

**Package layout.** Modules mirror Eq. (2): `perceive/`, `decide/`, `act/`, `reflect/`, `remember/`, plus internal `pipeline/turn_pipeline.py` exposing `execute_act_reflect` and `authorize_plan`.

**Environment.**

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
cp .env.example .env
ollama pull llama3 && tl-guard doctor
```

Key variables: `TL_GUARD_LLM`, `TL_GUARD_MODEL`, `TL_GUARD_OLLAMA_BASE_URL` (`http://127.0.0.1:11434` locally; `http://host.docker.internal:11434` in Compose).

**Interfaces.** The Student Buddy selects course/concept and chats in any supported language, displaying $(\ell_t,i_t,\tau_a,\omega_t,p_t)$. The Teacher Console edits $M$ via checkboxes/YAML and resolves escalations.

### 4.2 Execution Procedure

The practical implementation of the proposed framework has the following execution procedure.

**Step 1.** Session creation. The client posts `{course_id, concept}`. The agent loads LSM $M$ for the course and initializes $s_0$ with $p_0=0.30$, $H_0=\emptyset$, $r_0=0$, $w_0=0$.

**Step 2.** Student turn. The client posts `{message: u_t}` to `/sessions/{id}/turns` (or uses Streamlit/CLI). The agent executes `handle_turn`:

- *Step 2.1 (Perceive).* Compute $(\ell_t,\gamma_t,m_t)$ (Eq. 7); update $p_t$ (Eqs. 8–10); classify $i_t$ (Eqs. 11–14).
- *Step 2.2 (Decide).* Compute $\tau_d$ (Eq. 15), clamp $\tau_a$ (Eq. 4), select $\ell_r$, form plan $\pi_t$ (Eq. 16).
- *Step 2.3 (Act).* If $\mathrm{auth}_t=0$, return $\rho(\ell_r)$. Else generate $a^{\mathrm{raw}}_t$ (Eq. 18) via Ollama.
- *Step 2.4 (Reflect).* Compute $\lambda$ (Eq. 19) and $\omega_t$ (Eq. 20); rewrite/block/escalate as required; update $r_t$ (Eq. 21); optionally enqueue teacher review.
- *Step 2.5 (Remember).* Persist `TurnRecord` and $s_{t+1}$ (Eq. 22).

**Step 3.** Teacher policy update. An authenticated teacher (UI or `PUT /policies/{course_id}`) updates $M$ and $\mathcal{E}$ on disk. The in-memory agent cache is cleared so the next student turn loads the new policy.

**Step 4.** Escalation resolution. Teachers list open escalations, add a resolution note, and mark resolved. This does not automatically alter past student messages; it informs subsequent policy tightening.

**Step 5.** Health verification. `tl-guard doctor` probes Ollama `/api/tags` and a one-sentence completion to validate Act connectivity before demos.

**Illustrative scenario.**

**Table 4.** Three-turn execution trace (Python / loops, `python_intro` LSM).

| $t$ | $u_t$ (abbrev.) | $\ell_t$ | $i_t$ | $\tau_a$ | $\omega_t$ |
|---|---|---|---|---|---|
| 0 | How do I write a for loop? | en | none | $T_3$ | SAFE |
| 1 | loops का मतलब? समझाओ | mixed/hi | legitimate | $T_2$ (clamped) | SAFE |
| 2 | FULL SOLUTION / पूरा कोड | mixed | adversarial | $T_1$ | ESCALATE |

At $t=2$, the student still receives a safe $T_1$ hint while the teacher queue receives $(u_2,a^{\mathrm{raw}}_2,\mathrm{reason})$.

### 4.3 Performance Evaluation

In this section, we provide a performance evaluation of the proposed agentic framework. We define metrics analogous in spirit to overhead metrics in systems papers [reference style as in editable-blockchain evaluation], adapted to pedagogical policy enforcement.

#### 4.3.1 Metric Definitions

***Policy Compliance Rate ($C$).*** Fraction of LSM cells for which the engine’s authorize/deny decision matches $M$ (Eq. 23). Unit: dimensionless in $[0,1]$.

***Clamp Correctness.*** Fraction of over-request cases $(\ell,\tau_d)$ with $M_{\ell,\tau_d}=0$ for which Eq. (4) returns the maximal feasible tier (or correctly refuses).

***Leakage Score ($\lambda$).*** Continuous Reflect signal in $[0,1]$ (Eq. 19). Higher values indicate over-disclosure risk.

***Scaffold Integrity.*** Empirical rate of turns with $\omega_t=\mathrm{SAFE}$ or successful $\mathrm{REWRITE}$ that remain within $\tau_a$.

***Intent Macro-F1 (planned).*** Standard multi-class F1 on $\{legitimate,adversarial,neutral\}$.

***Mastery Gain (planned).*** $\Delta p = p_T - p_0$ under comparative conditions.

***False Suppression Rate (planned).*** Fraction of human-labeled legitimate L2 turns incorrectly blocked or over-tightened.

#### 4.3.2 Experimental Result on LSM Policy Compliance

In the first set of experiments, we validate every $(\ell,\tau)$ cell across three course configs (`python_intro`, `linear_algebra`, `general_science`), each with $|L|=5$ and $|\mathcal{T}|=4$, yielding $N=60$ cells.

**Table 5.** Effect of course configuration on policy compliance.

| Course Config | Cells $N$ | Correct | $C$ |
|---|---|---|---|
| `python_intro` | 20 | 20 | 1.00 |
| `linear_algebra` | 20 | 20 | 1.00 |
| `general_science` | 20 | 20 | 1.00 |
| **Aggregate** | **60** | **60** | **1.00** |

It is observed that compliance remains $C=1.00$ across all configurations. The engine correctly authorizes `true` cells, rejects `false` cells, and applies Eq. (4) clamping (e.g., Hindi $T_3$ request → $T_2$).

#### 4.3.3 Experimental Result on End-to-End Agent Behaviour

In the second set of experiments, automated tests inject a FakeLLM double (production still uses Ollama) and execute: (i) language detection for English, Hindi, and code-mixed inputs; (ii) BKT updates; (iii) legitimate vs adversarial intent cases; (iv) Act refusal when $\mathrm{auth}_t=0$; (v) a three-turn translanguaging session matching Table 4. All 11 automated tests pass. Provider resolution defaults to `OllamaLLM` when `TL_GUARD_LLM=ollama`.

#### 4.3.4 Discussion, Limitations, and Threats to Validity

Results indicate that agent-native Decide/Reflect mechanisms can enforce language-aware scaffolding without eliminating legitimate L2 clarification (Table 4, $t=1$). Limitations include: heuristic LIC; simulation-heavy evaluation pending classroom IRB study; three language pairs; surface-level cultural checks; variance of local LLM quality by language. Threats to validity: keyword-based $\mathbb{I}_{\mathrm{full}}$ may over/under-estimate leakage; FakeLLM may not reproduce all live-model failure modes; internal validity of planned E3 requires matched personas and human annotation.

---

## 5 Conclusion and Future Work

In this paper, we proposed TL-Guard, an agentic framework for guardrailed multilingual tutoring under pedagogical safety constraints. Motivated by the tension between translanguaging pedagogy and English-centric safety systems, we formalized an LSM policy matrix $M$, a five-stage agent loop (Eq. 2), BKT mastery updates (Eqs. 8–10), intent scoring (Eqs. 11–14), leakage scoring (Eq. 19), and disclosure contracts that mitigate cross-lingual leakage (Eq. 1). Practical implementation on Python/Ollama/FastAPI/Streamlit demonstrates 100% LSM compliance ($C=1$ over 60 cells) and correct end-to-end behaviour on legitimate and adversarial trajectories.

Future work includes: (i) IRB-approved classroom deployment; (ii) learned intent classifiers trained on annotated translanguaging corpora; (iii) extension to Tamil, Telugu, Mandarin, and additional Indian languages; (iv) voice-based translanguaging; (v) adaptive LSM updates from teacher corrections; and (vi) integration with trajectory-level cross-lingual risk monitoring.

---

## References

[1] García, O., Johnson, S. I., & Seltzer, K. (2017). *The Translanguaging Classroom.* Caslon Publishing.

[2] García, O. (2009). *Bilingual Education in the 21st Century.* Wiley-Blackwell.

[3] García, O., & Li Wei. (2014). *Translanguaging: Language, Bilingualism and Education.* Palgrave Macmillan.

[4] Cummins, J. (1979). Linguistic Interdependence and the Educational Development of Bilingual Children. *Review of Educational Research*, 49(2), 222–251.

[5] Cummins, J. (2000). *Language, Power and Pedagogy.* Multilingual Matters.

[6] KiKo-Prim. (2026). AI-Supported Translanguaging in Primary School. *Technology, Knowledge and Learning*, Springer.

[7] Walter. (2026). AI-Powered Learning Buddy for Non-Native English Speakers. *Asia Pacific Journal of Educators and Education*.

[8] GurukulAI. (2026). Hindi–English NCERT-Aligned Tutoring Using LLaMA 3.1 8B with RAG. *arXiv preprint*.

[9] Acharjo. (2025). Regionalized StudentGPT. *ISJEM*.

[10] SafeTutors. (2026). Pedagogical Harm in Multi-Turn AI Tutoring. *ACL ARR*.

[11] SHAPE. (2026). Graph-Augmented Mastery-Aware Tutoring Pipeline. *ACL*.

[12] Rebedea, T., et al. (2023). NeMo Guardrails. *arXiv:2310.10501*.

[13] Deng, Y., et al. (2024). MultiJail. *NAACL*.

[14] CSRT. (2025). Code-Switching Red-Teaming. *ACL*.

[15] 7S Samiti. (2025). AI Tutor for Rural India. *Deployment report*.

[16] Simulating LLM-to-LLM Multilingual Math Tutoring. (2025). *arXiv preprint*.

[17] Auditable Release Control. (2026). *arXiv preprint*.

[18] Translanguaging in STEM Meta-Synthesis. (2026). *Education Sciences (MDPI)*.

[19] EvalGuard Education Agent. (2026).

[20] Indian Multilingual Prompt Injection. (2026). *Scientific Reports*.

[21] Corbett, A. T., & Anderson, J. R. (1994). Knowledge Tracing. *UMUAI*, 4(4), 253–278.

[22] Venable, J., Pries-Heje, J., & Baskerville, R. (2016). FEDS. *EJIS*, 25(1), 77–89.

---

## Appendix A: Example LSM ($M$) for `python_intro`

$$
\begin{array}{c|cccc}
 & T_1 & T_2 & T_3 & T_4 \\ \hline
\mathrm{en} & 1 & 1 & 1 & 0 \\
\mathrm{hi} & 1 & 1 & 0 & 0 \\
\mathrm{bn} & 1 & 1 & 0 & 0 \\
\mathrm{es} & 1 & 1 & 1 & 0 \\
\mathrm{mixed} & 1 & 1 & 0 & 0 \\
\end{array}
$$

## Appendix B: System Prompt Composition (Eq. 6)

```
Σ_stance: Translanguaging welcome; never punish language mixing.
Σ_tier(T1): short nudge only; no full code/answer.
Σ_tier(T2): conceptual explanation; no full solution.
Σ_tier(T3): worked example; omit final boxed answer if possible.
Σ_tier(T4): full solution allowed; still teach.
Σ_lang: Respond in {en|hi|bn|es|mixed}.
Σ_ctx: Course={c}, Concept={k}.
```
