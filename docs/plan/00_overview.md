# **Demo Gauntlet — MVP Implementation Plan**

This document defines the **phased implementation plan** for the Demo Gauntlet MVP.
Each phase is decomposed into **atomic components** so development can be executed, tested, and validated incrementally.

---

# 🚀 **Overview**

**Goal:**
Create an MVP simulation environment where a Solution Consultant (SC) uploads a demo deck, the system generates truth-based challenges, and the SC responds to those challenges slide-by-slide.
Responses are **evaluated** against **pre-generated ideal answers**.

**Interaction mode for MVP:**
**Text-only responses** (voice added in V2).

---

# 📁 **Project Structure (High-Level)**

```
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
```

---

# 🧱 **Phase 0 — Project & Environment Setup**

### **0.1 Repository Scaffolding**

* Initialize repo
* Add `backend/`, `frontend/`, `data/` folders
* Create `pyproject.toml` or `requirements.txt`
* Add `.gitignore` (venv, .env, data artifacts)

### **0.2 Base Environment**

* Configure virtual environment
* Add configuration loader (`config.py`)
* Select frameworks:

  * **Backend:** FastAPI or Flask
  * **UI:** Streamlit or React+Flask
* Install dependencies:

  * `sentence-transformers`
  * `faiss` or `chromadb`
  * search API client (Brave/SerpAPI)
  * `python-pptx`, `pdfplumber`
