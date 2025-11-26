Demo Gauntlet — MVP Implementation Plan

This document defines the phased implementation plan for the Demo Gauntlet MVP.
Each phase is decomposed into atomic components so development can be executed, tested, and validated incrementally.

🚀 Overview

Goal:
Create an MVP simulation environment where a Solution Consultant (SC) uploads a demo deck, the system generates truth-based challenges, and the SC responds to those challenges slide-by-slide.
Responses are evaluated against pre-generated ideal answers.

Interaction mode for MVP:
Text-only responses (voice added in V2).

📁 Project Structure (High-Level)
/demo-gauntlet-mvp
    /backend
        /ingestion
        /research
        /challenges
        /evaluation
        /session
        /models
    /frontend
        /ui
        /static
    /data
        /sessions
        /avatars
        /decks
    plan.md
    README.md

🧱 Phase 0 — Project & Environment Setup
0.1 Repository Scaffolding

Initialize repo

Add backend/, frontend/, data/ folders

Create pyproject.toml or requirements.txt

Add .gitignore (venv, .env, data artifacts)

0.2 Base Environment

Configure virtual environment

Add configuration loader (config.py)

Select frameworks:

Backend: FastAPI or Flask

UI: Streamlit or React+Flask

Install dependencies:

sentence-transformers

faiss or chromadb

search API client (Brave/SerpAPI)

python-pptx, pdfplumber

🧩 Phase 1 — Deck Ingestion & Slide Mapping
1.1 Upload Handler

Endpoint: POST /upload-deck

Save raw file → data/decks/{session_id}/

1.2 Slide Extraction

PDF → page text

PPTX → slide text + speaker notes

Output JSON structure per slide:

{
  "index": 0,
  "title": "Slide Title",
  "raw_text": "Slide content text",
  "notes": "Optional speaker notes"
}

1.3 Chunking

Split based on:

bullets

headings

sentence boundaries

Enforce max token/char size

1.4 Slide Tagging

Tag categories:

architecture, cost, security, integration,
workflow, value, compliance

Lightweight keyword-based tagging

1.5 Embedding + Vector Store

Generate embeddings for each chunk

Store:

{
  "chunk_id": "uuid",
  "slide_index": 0,
  "text": "chunk text",
  "tags": ["architecture"],
  "embedding": [...]
}

1.6 Tests

PDF extraction test

PPTX extraction test

Chunk size test

Tag accuracy test

🔍 Phase 2 — Research Agent (Truth Layer)
2.1 Query Builder

Derive 3–5 research queries from:

deck title

repeated terms

industry keywords

2.2 Search Client

Brave or SerpAPI wrapper

Normalized results: {title, url, snippet}

2.3 Research Summarizer

Generate research_dossier.json:

competitor insights

cost/ROI themes

security/compliance notes

implementation pitfalls

2.4 Tests

Mock search → expected dossier fields

No-result fallback

🧩 Phase 3 — Challenger Definitions (Static)
3.1 Challenger Schema

3 challengers in MVP:

CTO (architecture/integration/scale)

CFO (cost/value/ROI)

Compliance/Risk (security/compliance)

3.2 Domain Tag Mapping

Mapping slide tags → challenger relevance.

3.3 Tests

Validate challenger JSON loads correctly

Validate domain tag sets

⚙️ Phase 4 — Challenge-Set Generation
4.1 Data Models

Define:

Question

IdealAnswer

ChallengeItem

4.2 Relevance Engine

For each slide:

Challenger relevance if domain tags intersect

4.3 Question Generation

Use deck chunks + research truths

1–2 questions per challenger per relevant slide

Must reference:

slide claim

research fact

4.4 Ideal Answer Generation

Truth-based “best answer” per question.

4.5 Scoring Rubric

Rubric with weights:

accuracy

completeness

truth_alignment

clarity

4.6 Challenge Set Builder

Generate full challenge-set:

/session/{id}/challenges.json

4.7 Tests

Relevance logic test

ChallengeItem validation test

🖥️ Phase 5 — Demo Room UI
5.1 Flow

Upload deck

Processing screen

Enter Demo Room

5.2 Slide Viewer

Next/Prev controls

Display title + text

Track current_slide_index

5.3 Challenger Avatars

Static images placed around slide:

CTO (top-left)

CFO (top-right)

Compliance (bottom-right)

5.4 Challenge Display Logic

On slide change:

Backend returns 0–2 challenges

Randomized with trigger probabilities

If triggered → show speech bubble

5.5 Response Input

Single text area:

[ Type your answer here... ] [Submit]

5.6 Tests

Navigation tests

Speech bubble mapping tests

🧮 Phase 6 — Scoring & Evaluation Engine
6.1 Encoding

Reuse embedding model

Encode SC answer + ideal answer

6.2 Similarity + Heuristics

Compute:

cosine similarity

completeness (keyword coverage)

clarity (length + relevance)

Apply rubric weights → score 0–100.

6.3 Persistence

Store interactions:

{
  "slide_index": 1,
  "challenger_id": "cto",
  "question_id": "q123",
  "user_answer": "...",
  "score": 78
}

6.4 UI Feedback

MVP:
Show a small badge next to the question:

Good

Okay

Weak

6.5 Tests

Identical answers → high score

Non-relevant answers → low score

📊 Phase 7 — Session Summary & Reporting
7.1 Aggregation

Compute:

average challenger scores

slide-by-slide scores

overall readiness score

7.2 Report Output

Display:

Overall score gauge

Three challenger cards

Top 3 strengths

Top 3 gaps

7.3 Export (Optional MVP)

JSON export only.

7.4 Tests

Synthetic session → correct report aggregation.

⚠️ Phase 8 — Logging & Guardrails
8.1 Logging

Capture:

deck ingestion

challenge generation

evaluation steps

session completion

8.2 Fallback Mechanisms

If research fails:

deck-only questions
If LLM call fails:

generic challenge templates

8.3 Config Toggles

Add flags for:

enable_research

max_challengers

max_questions_per_slide

🎯 MVP Complete When:

Deck upload works

Slide ingestion + chunking works

Research dossier generated

3 challengers produce questions/ideal answers

Demo Room UI loads

Randomized challenges appear per slide

SC answers evaluated & scored

End-of-session summary produced


