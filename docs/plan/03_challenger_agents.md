# 🧩 **Phase 3 — Challenger Definitions & Agents**

### **3.1 Challenger Schema**

3 initial challengers in MVP (more configurable via admin):

* CTO (architecture/integration/scale)
* CFO (cost/value/ROI)
* Compliance/Risk (security/compliance)

### **3.2 Domain Tag Mapping**

Mapping slide tags → challenger relevance.

### **3.3 Challenger as AI Agent (Reasoning-Capable)**

Each challenger is implemented as a **fully independent AI agent** with its own reasoning, context, evidence, and scoring behavior. There is **no shared brain**; each challenger makes its own decisions.

#### **Agent Contract (Interface)**

All challengers must implement the following interface:

```python
class ChallengerAgent(Protocol):
    id: str
    name: str
    role: str
    domain_tags: list[str]
    agent_prompt: str

    def precompute_challenges(
        self,
        slides: list[Slide],
        deck_retriever: Retriever,
        fact_store: FactStore,
    ) -> list[ChallengeItem]:
        """
        Offline reasoning step:
        - Retrieve slide-relevant deck chunks (via embeddings)
        - Retrieve relevant research facts
        - Decide which issues matter
        - Generate grounded questions
        - Generate ideal answers
        - Generate rubrics
        Returns a list of ChallengeItem objects for THIS agent only.
        """

    def decide_questions_for_slide(
        self,
        slide_index: int,
        challenge_items: list[ChallengeItem],
    ) -> list[ChallengeItem]:
        """
        Online reasoning step:
        - For the current slide, this agent alone decides whether to speak,
          based on its own evidence, relevance, and trigger probabilities.
        - Chooses 0–N questions from its own challenge set.
        """

    def evaluate_response(
        self,
        question: ChallengeItem,
        user_answer: str,
    ) -> EvaluationResult:
        """
        Online reasoning step:
        - This agent evaluates the user's answer using:
            • its own ideal answer
            • its own rubric
            • its own interpretation of accuracy, truth alignment, completeness
        - Returns a per-agent evaluation.
        """
```

#### **Agent Reasoning Loops**

Each challenger performs reasoning in **two stages**:

##### **A. Offline (during context loading)**

Each challenger:

* Retrieves relevant deck chunks
* Retrieves relevant research facts
* Decides which claims matter
* Forms its own worldview of the deck
* Generates:

  * grounded questions
  * grounded ideal answers
  * its own scoring rubric

##### **B. Online (during the simulation)**

On each slide, each challenger independently:

* Observes slide context
* Decides whether to fire a question
* Selects ONE of its precomputed questions
* Scores the user's response using its own rubric & evidence

This ensures:

* independent reasoning,
* no cross-contamination between agents,
* realism (each agent argues from its own evidence set),
* future compatibility with CrewAI or any other agent framework.

### **3.4 Challenger Agent Prompt Templates (to be implemented)**

Each challenger includes a structured persona prompt:

* role + behavioral tone
* reasoning rules
* evidence usage rules
* grounding expectations
* question style
* evaluation style

Templates will be added for:

* CTO Agent
* CFO Agent
* Compliance/Risk Agent
* Any custom user-defined challenger

### **3.5 Challenger Management (Edit/Add) (Edit/Add)**

* Define a `ChallengerConfig` model and JSON schema for challengers:

  * id, name, role, domain_tags, description, weightings, agent_prompt
* Implement a backend module `challenger_store.py` to:

  * load challengers from `data/challengers.json`
  * add a new challenger definition
  * update an existing challenger
  * validate domain_tags and weightings
* Add API endpoints:

  * `GET /challengers` – list all challengers
  * `POST /challengers` – add a new challenger
  * `PUT /challengers/{id}` – update an existing challenger
* Add a simple admin UI section (MVP):

  * Table of challengers
  * Form to add a new challenger
  * Edit form for existing challengers (name, role, description, domain_tags, weights, agent_prompt)
* Ensure new challengers are automatically picked up by the challenge-set generation pipeline (no code changes required beyond reload).

### **3.5 Challenger Management Tests****

* Adding a valid challenger persists correctly
* Updating an existing challenger maintains referential integrity
* Challenge-set generation works after adding or editing challengers

### **3.6 Challenger Avatar Generation (Image LLM Integration)**

* Define an `AvatarSpec` model for each challenger:

  * challenger_id, style_preset, base_prompt, emotional_states (e.g., neutral, skeptical, impressed)
* Implement an `image_provider` abstraction layer to call an image-generation LLM (e.g., Google image model, Stable Diffusion, etc.):

  * `generate_avatar(challenger_id, state) -> image_path`
  * Provider and API keys configured via `config.py` / environment
* Add backend job/endpoint:

  * `POST /challengers/{id}/generate-avatars` – generate avatar images for all defined emotional_states and store under `data/avatars/{challenger_id}/`
* Frontend wiring:

  * Challenger admin UI exposes a "Generate Avatars" button per challenger
  * Demo Room UI loads avatars from `data/avatars/{challenger_id}/` with graceful fallback to static placeholders if missing
* Ensure avatar generation is *optional* for core MVP flow but available when an image model is configured.

### **3.7 Avatar Generation Tests**

* Mock image provider: verify we call it with the correct prompts and parameters
* Verify generated file paths are saved and resolvable by the UI
* Verify system falls back to default static avatars if dynamic avatars are not available or generation fails
