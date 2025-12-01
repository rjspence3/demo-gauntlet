# 🔍 **Phase 2 — Research Agent (Truth Layer)**

**Purpose:** Build a *Deep Research Agent* that expands the deck’s claims using real-world evidence gathered from web search. This forms a structured “truth layer” that challengers must ground their reasoning and questions in. The agent operates entirely during preprocessing.

### **2.1 Topic Extraction from Deck**

* Parse `slides[]` to extract relevant research topics:

  * product/module names
  * competitor names
  * industry/domain terms (ITSM, ERP, healthcare, etc.)
  * architecture keywords (multi-tenant, microservices)
  * cost/ROI language
  * security/compliance language
* Build a deduplicated `research_topics[]` list.

### **2.2 Search Query Builder**

* For each topic, generate 1–2 web search queries.
* Queries must be optimized for Brave/SerpAPI.
* Examples:

  * "ITSM license utilization benchmark 2024"
  * "integration challenges with SAP ECC modern SaaS"
  * "SaaS SOC2 data residency EU requirements"

### **2.3 Web Search Client**

* Call Brave/SerpAPI for each query.
* Normalize search results into:

```json
{
  "title": "...",
  "url": "...",
  "snippet": "...",
  "source": "domain.com"
}
```

* Deduplicate by URL/domain.
* Keep up to `N` results per topic.

### **2.4 Fact Clustering & Summarization (Deep Research Agent)**

* Group search results by thematic categories aligned with challenger domains:

  * pricing/ROI
  * architecture/integration
  * implementation pitfalls
  * security/compliance
  * competitive landscape
* Summarize each cluster into **grounded facts** using an LLM:

  * Each fact must:

    * reflect real content from snippets
    * avoid hallucination
    * be expressed neutrally
    * include source metadata
* Fact format:

```json
{
  "id": "fact_001",
  "topic": "integration",
  "text": "Customers report difficulty integrating with legacy SAP ECC unless middleware is used.",
  "source_url": "https://example.com",
  "source_title": "Integration Pitfalls with SaaS",
  "domain": "example.com",
  "snippet": "One recurring challenge is connecting to older SAP..."
}
```

### **2.5 Research Dossier Output**

* Save final structured output to: `data/sessions/{id}/research_dossier.json`
* The dossier is the **official truth layer**.
* All challengers MUST ground their questions and ideal answers in:

  * deck chunks
  * dossier facts

### **2.6 FactStore Access Layer**

Implement:

```python
class FactStore:
    def get_facts_by_topic(self, topic: str) -> list[Fact]: ...
    def search_facts(self, query: str, k: int = 5) -> list[Fact]: ...
```

Used by challengers during reasoning.

### **2.7 Rules for Challenger Usage**

* Challengers may ONLY ask questions grounded in:

  * retrieved deck chunks, AND/OR
  * retrieved research facts.
* Every question must include:

```json
{
  "based_on_chunks": [...],
  "based_on_facts": [...]
}
```

* No grounding = the question is invalid.

### **2.8 Tests**

* Search client produces normalized results
* Dossier contains only grounded facts with sources
* Challengers cannot produce ungrounded questions (enforced by tests)
* FactStore retrieval accuracy
  **
* Mock search → expected dossier fields (including source metadata)
* No-result fallback: dossier still exists with empty `facts` list and pipeline degrades gracefully
* Mock search → expected dossier fields
* No-result fallback
