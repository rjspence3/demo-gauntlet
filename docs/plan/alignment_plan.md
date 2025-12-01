# Alignment Plan: Challenger Agents & Architecture

## Goal Description
Address the gaps identified between the codebase and the plan documents (`03_challenger_agents.md`, `08_technical_standards.md`). Specifically, implement the missing **Challenger Management**, **Avatar Generation**, and correct the **Offline/Online Reasoning** flow.

## User Review Required
> [!IMPORTANT]
> This plan shifts the "Challenge Generation" from a per-slide online process (current) to a **pre-computation** step (planned). This means users will see a "Preparing Simulation..." loading state before entering the Demo Room, but the Demo Room itself will be faster and more consistent.

## Proposed Changes

### 0. Ingestion & Parsing (Phase 1.2)
#### [MODIFY] [backend/ingestion/parser.py](file:///Users/rob/Development/demoGauntlet/backend/ingestion/parser.py)
- **Current:** Basic `pdfplumber` and `python-pptx` extraction.
- **Missing:** OCR for image-heavy slides and PDF fallback for complex PPTX.
- **Plan:** Add `pdf2image` + `pytesseract` (or similar) for OCR support. Implement `libreoffice` or similar conversion for PPTX->PDF fallback if extraction fails (optional for strict MVP, but noted as gap).
- **Action:** Add `_extract_with_ocr` method and integrate into `extract_from_file`.

### 1. Challenger Management (Phase 3.5)
#### [NEW] [backend/challenges/store.py](file:///Users/rob/Development/demoGauntlet/backend/challenges/store.py)
- Implement `ChallengerStore` to load/save personas from `data/challengers.json`.
- Support adding/editing personas via API.

#### [NEW] [backend/api/routers/challengers.py](file:///Users/rob/Development/demoGauntlet/backend/api/routers/challengers.py)
- `GET /challengers`: List all.
- `POST /challengers`: Create new.
- `PUT /challengers/{id}`: Update.

### 2. Avatar Generation (Phase 3.6 & 8.10)
#### [NEW] [backend/challenges/avatars.py](file:///Users/rob/Development/demoGauntlet/backend/challenges/avatars.py)
- Implement `AvatarGenerator` using an image provider (mock for now, extensible to OpenAI/Stable Diffusion).
- Generate avatars for states: `neutral`, `skeptical`, `impressed`, `thoughtful`.

#### [MODIFY] [backend/models/core.py](file:///Users/rob/Development/demoGauntlet/backend/models/core.py)
- Update `ChallengerPersona` to include `avatar_paths: Dict[str, str]`.

### 3. Scoring Engine (Phase 6)
#### [MODIFY] [backend/evaluation/engine.py](file:///Users/rob/Development/demoGauntlet/backend/evaluation/engine.py)
- **Current:** `clarity` score is hardcoded to 90. `completeness` is a simple length ratio.
- **Plan:** Implement a real clarity heuristic (e.g., Flesch-Kincaid readability score or LLM-based eval).
- **Action:** Replace hardcoded 90 with a basic readability check or an LLM call if budget permits.

### 4. Reasoning Architecture (Phase 3.3)
#### [MODIFY] [backend/challenges/generator.py](file:///Users/rob/Development/demoGauntlet/backend/challenges/generator.py)
- Ensure `precompute_challenges` handles the entire deck and stores results in `SessionStore`.

#### [MODIFY] [backend/api/routers/research.py](file:///Users/rob/Development/demoGauntlet/backend/api/routers/research.py)
- Add `POST /session/{id}/precompute`: Triggers full challenge generation for selected personas.

#### [MODIFY] [frontend/src/components/ChallengerSelection.tsx](file:///Users/rob/Development/demoGauntlet/frontend/src/components/ChallengerSelection.tsx)
- On "Start Simulation", call `/precompute` endpoint.
- Show a loading state ("Briefing Challengers...") before navigating to Demo Room.

#### [MODIFY] [frontend/src/components/DemoRoom.tsx](file:///Users/rob/Development/demoGauntlet/frontend/src/components/DemoRoom.tsx)
- Remove `generateChallenges` call from `useEffect`.
- Instead, fetch *all* challenges for the session on mount.
- Use `decide_questions_for_slide` (logic moved to frontend or lightweight backend call) to trigger bubbles.

## Verification Plan

### Automated Tests
- `test_challenger_store.py`: Verify CRUD operations for personas.
- `test_precompute_flow.py`: Verify challenges are generated and stored for all slides.

### Manual Verification
1.  **Challenger Management**: Use `curl` or Swagger UI to add a new "Pirate CFO" persona. Verify it appears in the Selection screen.
2.  **Precompute Flow**: Select challengers -> Click Start -> Verify "Briefing..." loader -> Enter Demo Room.
3.  **Demo Room**: Verify challenges appear instantly (no "Analyzing..." delay) as they are precomputed.
