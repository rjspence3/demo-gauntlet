# Design Document

## 1. System Architecture

### High-Level Overview
The Demo Gauntlet is a web application that simulates a "gauntlet" of challenges for a Solution Consultant (SC) based on an uploaded demo deck.
- **Frontend**: React + Vite (Single Page Application).
- **Backend**: FastAPI (Python).
- **Data Storage**: Local filesystem (JSON/ChromaDB) for MVP.
- **AI/ML**: Sentence Transformers for embeddings, LLM (via API) for challenge generation.

### Module Boundaries
- `backend.ingestion`: Handles file parsing (PDF/PPTX) and chunking.
- `backend.research`: Handles external search and dossier generation.
- `backend.challenges`: Generates questions and ideal answers.
- `backend.evaluation`: Scores user responses.
- `backend.session`: Manages session state.

## 2. API Contracts

### Ingestion
- **POST /ingestion/upload**
    - **Input**: `Multipart/Form-Data` (file)
    - **Output**:
      ```json
      {
        "session_id": "uuid",
        "filename": "deck.pptx",
        "slide_count": 12,
        "status": "processed"
      }
      ```
    - **Errors**: 400 (Invalid file type), 500 (Processing failed)

### Research
- **POST /research/generate/{session_id}**
    - **Output**: `ResearchDossier` (JSON)

### Challenges
- **GET /challenges/personas**
    - **Output**: `List[ChallengerPersona]` (JSON)
- **POST /challenges/generate**
    - **Input**: `{ "session_id": str, "persona_id": str }`
    - **Output**: `List[Challenge]` (JSON)

### Session
- **GET /session/{session_id}**
    - Output: `SessionState` (JSON)

## 3. Data Models

### ResearchDossier
```python
@dataclass
class ResearchDossier:
    session_id: str
    competitor_insights: List[str]
    cost_benchmarks: List[str]
    compliance_notes: List[str]
    implementation_risks: List[str]
    sources: List[str]

### ChallengerPersona
```python
@dataclass
class ChallengerPersona:
    id: str
    name: str
    role: str
    style: str # e.g., "aggressive", "curious"
    focus_areas: List[str] # e.g., ["cost", "security"]
```

### Challenge
```python
@dataclass
class Challenge:
    id: str
    session_id: str
    persona_id: str
    question: str
    context_source: str # e.g., "slide 5", "research"
    difficulty: str # "easy", "medium", "hard"
```

### Slide
```python
@dataclass
class Slide:
    index: int
    title: str
    text: str
    notes: str = ""
    tags: List[str] = field(default_factory=list)
```

### Chunk
```python
@dataclass
class Chunk:
    id: str
    slide_index: int
    text: str
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Challenge
```json
{
  "id": str,
  "challenger_type": "CTO" | "CFO" | "Compliance",
  "question": str,
  "ideal_answer": str
}
```
