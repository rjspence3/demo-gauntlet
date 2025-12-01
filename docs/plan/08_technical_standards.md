# ⚙️ **Phase 8 — Technical Standards & Advanced Specifications**

These sections define the best‑practice implementations for the remaining architectural areas: retrieval, scoring, error handling, agent memory, challenger conflicts, avatar emotion mapping, persona editing, image generation, and preprocessing budgets.

---

## **8.1 LLM Backend Abstraction**

* Introduce `LLMClient` interface with:

  * `complete(prompt) -> str`
  * `complete_structured(prompt, schema) -> dict`
  * `health_check() -> bool`
* Implement `OpenAIClient` as first provider.
* Future providers: Anthropic, local (Ollama), mock for tests.
* All LLM interactions (research, challengers, rubric, ideal answers) must go through this abstraction.

---

## **8.2 Ideal Answer Generation Standard**

**Purpose:** Establish deterministic, grounded ideal responses.

**Structure:**

```json
{
  "question_id": "q123",
  "challenger_id": "cto",
  "text": "…ideal grounded answer…",
  "key_points": ["point1", "point2"],
  "evidence": {
    "chunks": ["chunk_01"],
    "facts": ["fact_002"]
  },
  "tone": "concise-technical"
}
```

**Rules:**

* Must reference only allowed evidence.
* Must answer the question directly.
* Must avoid hallucination.
* Must include 3–6 key points.
* Tone depends on challenger type.

---

## **8.3 Question Style & Template Rules**

**Hard rules:**

* Must be grounded in evidence.
* Single focus per question.
* Professional enterprise tone.
* Explicitly reference deck claims / facts.

**Templates:**

* Claim Verification
* Risk Exposure
* Cost/ROI Challenge
* Technical Depth Check
* Implementation Reality Check
* Competitive Objection

Questions stored as:

```json
{
  "question_id": "q_cto_01",
  "challenger_id": "cto",
  "text": "…",
  "based_on_chunks": ["chunk_07"],
  "based_on_facts": ["fact_002"],
  "template_used": "A"
}
```

---

## **8.4 Trigger Probability Rules (When Challengers Speak)**

Trigger probability per challenger per slide is computed as:

```
base_p = 0.15 + 0.35*relevance_score + 0.35*evidence_score
```

Boundaries:

* 0–85% per challenger.
* `MAX_QUESTIONS_PER_SLIDE = 2`
* `MAX_QUESTIONS_PER_CHALLENGER = 6`

If multiple challengers fire, pick highest probability until reaching cap.

---

## **8.5 Retrieval Standards (DeckRetriever + FactStore)**

**DeckRetriever:**

```python
get_nearest_chunks(query, k=5)
get_chunks_for_slide(slide_index)
```

**FactStore:**

```python
get_facts_by_topic(topic, limit=5)
search_facts(query, limit=5)
```

All challenger reasoning must access deck + research through these abstraction layers.

---

## **8.6 Scoring Calibration & Normalization**

**Components:**

* Accuracy (embedding similarity)
* Completeness (key point coverage)
* Truth Alignment (heuristic)
* Clarity (length + structure)

**Default Weights:**

```
accuracy: 0.45
completeness: 0.35
clarity: 0.15
truth_alignment: 0.05
```

**Score buckets:**

* ≥ 80 → Good
* 50–79 → Okay
* <50 → Weak

---

## **8.7 Precompute Error Handling Rules**

* If web search fails → dossier exists with empty facts.
* If question generation fails → drop question.
* If challenger has zero usable questions → mark as inactive.
* Never allow ungrounded questions.

---

## **8.8 Challenger Memory & Session State**

**MVP:** stateless except for logging asked questions + scores.

**Future:** optional adaptive behavior (follow‑ups, escalation).

---

## **8.9 Multi‑Challenger Conflict Handling**

* Multiple challengers may fire on a slide.
* De‑duplicate near‑identical questions across challengers.
* SC answers them sequentially.
* UI shows separate speech bubbles.

---

## **8.10 Avatar Emotion State Mapping**

**States:** neutral, curious, skeptical, impressed, thoughtful.

**Mapping:**

* Score ≥ 80 → impressed
* 50–79 → thoughtful
* <50 → skeptical
* When challenger fires → curious
* Inactivity → neutral

---

## **8.11 Challenger Persona Editing Constraints**

User‑editable fields:

* name, role, description
* domain_tags
* weightings
* agent_prompt
* emotional avatar presets

Validation:

* domain_tags cannot be empty
* weightings must normalize to 1
* agent_prompt length limit (e.g., 2k chars)

---

## **8.12 Image Generation Storage & Caching Rules**

* Avatars stored under: `data/avatars/{challenger_id}/{state}.png`
* Cached until user triggers “regenerate.”
* On failure → use default static avatar.
* Prompts may not include PII or sensitive deck details.

---

## **8.13 Preprocessing Time & LLM Budget Limits**

**Time targets:**

* Total preprocessing ≤ 60 seconds
* Search calls ≤ 8s per query
* LLM calls ≤ 20s each

**LLM Budget:**

* Max research topics: 10
* Max search queries: 20
* Max summarization calls: 10
* Max challenge precompute calls per challenger: 10

If limits are hit → degrade gracefully; warn in challenge detail UI.

---

# 🎯 MVP now reflects complete best‑practice specifications.
