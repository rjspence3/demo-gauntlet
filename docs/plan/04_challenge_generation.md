# ⚙️ **Phase 4 — Challenge-Set Generation**

### **4.1 Data Models**

Define:

* `Question`
* `IdealAnswer`
* `ChallengeItem`

### **4.2 Relevance Engine**

For each slide:

* Challenger relevance if domain tags intersect

### **4.3 Question Generation (Evidence-Grounded)**

* Use **both** deck content and research facts:

  * Retrieve top-k deck chunks for the slide via embeddings
  * Retrieve top-k relevant `facts` from `research_dossier.json`
* For each eligible challenger/slide pair, generate 1–2 questions that:

  * Explicitly reference a **specific deck claim** (via chunk_id/slide_index)
  * Explicitly reference **one or more research facts** where applicable
* Each generated question must include a compact evidence map:

```json
{
  "question_id": "q123",
  "based_on_chunks": ["chunk_01", "chunk_07"],
  "based_on_facts": ["fact_002", "fact_005"]
}
```

* **Hard rule:** challengers must not ask questions that cannot be grounded in either deck chunks or research facts.

### **4.4 Ideal Answer Generation (Evidence-Grounded)**

* For each question, generate an ideal answer that:

  * Uses the same `based_on_chunks` and `based_on_facts` as its evidence set
  * Stays within what is supported by the deck and research
  * Clearly resolves the concern raised by the question
* Store ideal answer with explicit evidence references:

```json
{
  "question_id": "q123",
  "text": "ideal grounded answer…",
  "evidence": {
    "chunks": ["chunk_01", "chunk_07"],
    "facts": ["fact_002", "fact_005"]
  }
}
```

* This ensures evaluation later is comparing the SC’s answer against a **truth-bounded** response, not a free-form hallucinated answer.

### **4.5 Scoring Rubric**

Rubric with weights:

* accuracy
* completeness
* truth_alignment
* clarity

### **4.6 Challenge Set Builder**

Generate full challenge-set:

```json
/session/{id}/challenges.json
```

### **4.7 Tests**

* Relevance logic test
* ChallengeItem validation test
