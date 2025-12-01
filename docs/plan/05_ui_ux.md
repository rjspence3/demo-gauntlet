# 🖥️ **Phase 5 — Product-Grade UI (Screens + Wireframes)**

The MVP UI must look like a **professional, sale-ready application**. This section defines each screen, its purpose, its UX flow, and a textual wireframe.

---

## **5.0 Global UX Principles**

* Clean enterprise aesthetic (think Notion, Linear, ServiceNow Next Experience)
* Neutral color palette with strong contrast for clarity
* Consistent spacing (8px grid)
* Smooth slide transitions
* Clear typography hierarchy (H1, H2, body, meta)
* Modal-free flow wherever possible — linear, clean progressions
* No LLM or technical jargon exposed to end users

---

## **5.1 Screen: Deck Upload**

### **Purpose:**

Let users upload PPT/PPTX/PDF decks and start a new simulation.

### **Wireframe (textual):**

```
 -------------------------------------------------
|  +-------------------------------------------+  |
|  |        Upload Your Demo Deck              |  |
|  +-------------------------------------------+  |
|                                               |
|   [ Drag & Drop deck here ]                   |
|               or                              |
|        [ Select File Button ]                 |
|                                               |
|   Supported formats: PPTX, PPT, PDF           |
|                                               |
|                      [ Continue → ]           |
 -------------------------------------------------
```

### **Key UI Elements:**

* Large centered upload dropzone
* Progress indicator upon upload
* Auto-detect file type and validate
* If PPT/PPTX is too complex, soft message: "We will optimize extraction automatically"

---

## **5.2 Screen: Processing & Context Building**

### **Purpose:**

Show user that the system is ingesting slides, chunking, embedding, running research, and generating challenges.

### **Wireframe:**

```
 -------------------------------------------------
|  Building Your Simulation...                   |
|------------------------------------------------|
|  [✓] Deck uploaded                             |
|  [●] Extracting slides                         |
|  [ ] Chunking and embeddings                   |
|  [ ] Running deep research                     |
|  [ ] Generating challenger questions           |
|------------------------------------------------|
|           Animated progress bar                |
 -------------------------------------------------
```

### **Notes:**

* Use step-by-step checklist, progressively filling
* Should feel polished and trustworthy (like a CI pipeline visual)

---

## **5.3 Screen: Challenger Selection**

### **Purpose:**

Users choose which challengers will appear in the room.
System recommends challengers based on evidence richness.

### **Wireframe:**

```
 --------------------------------------------------------------
|  Choose Your Challengers                                     |
|--------------------------------------------------------------|
|  Recommended (based on evidence coverage):                   |
|  [ CTO ]   [ CFO ]   [ Compliance ]                          |
|--------------------------------------------------------------|
|  All Challengers:                                            |
|  ----------------------------------------------------------  |
|  | CTO (Architecture)       | Evidence: ████████  | [ View ]|
|  | CFO (Cost/ROI)           | Evidence: ██████    | [ View ]|
|  | Compliance/Risk          | Evidence: █████████ | [ View ]|
|  | Ops Lead (optional)      | Evidence: ████      | [ View ]|
|  | Competitive Analyst      | Evidence: ███████   | [ View ]|
|  ----------------------------------------------------------  |
|                                                                |
|                                   [ Start Simulation → ]       |
 --------------------------------------------------------------
```

### **Notes:**

* Evidence bar shows how many facts/questions were generated
* User can toggle challengers on/off
* System preselects strongest 2–3 challengers
* Each challenger row includes a **[ View ]** button that opens a Challenger Detail view (see 5.4)

---

## **5.4 Screen: Challenger Detail / Evidence Inspector**

### **Purpose:**

Let the user inspect exactly **what information each challenger has access to** and how it reasons, to build trust and transparency.

### **Wireframe:**

```
 --------------------------------------------------------------
|  Challenger: CTO (Architecture)                              |
|--------------------------------------------------------------|
|  [ Overview ] [ Deck Evidence ] [ Research Facts ] [ Q&A ]   |
|--------------------------------------------------------------|
|  Overview:                                                   |
|   - Role: Evidence-checking CTO                              |
|   - Domain tags: architecture, integration, scale            |
|   - Reasoning tools:                                         |
|       • retrieve_deck_chunks()                               |
|       • retrieve_research_facts()                            |
|       • score_response()                                     |
|--------------------------------------------------------------|
|  Deck Evidence (tab):                                        |
|   Table of referenced chunks:                                |
|   --------------------------------------------------------   |
|   | Slide | Excerpt                         | Tags        |  |
|   |  3    | "We integrate with anything"    | integration |  |
|   |  5    | "Scales to millions of users"   | scale       |  |
|   --------------------------------------------------------   |
|--------------------------------------------------------------|
|  Research Facts (tab):                                       |
|   List of facts used for this challenger with sources.       |
|--------------------------------------------------------------|
|  Q&A (tab):                                                  |
|   - Shows pre-generated questions and ideal answers          |
|   - Each row clickable to view evidence map (chunks+facts)   |
 --------------------------------------------------------------
```

### **Notes:**

* This screen is read-only and meant for **explainability**
* Makes it clear challengers are grounded in:

  * specific deck claims (chunks)
  * specific research facts with URLs
* Optional future enhancement: show a small "reasoning trace" of how the challenger arrives at a question.

---

| Choose Your Challengers                                        |                     |                     |         |
| -------------------------------------------------------------- | ------------------- | ------------------- | ------- |
| Recommended (based on evidence coverage):                      |                     |                     |         |
| [ CTO ]   [ CFO ]   [ Compliance ]                             |                     |                     |         |
| -------------------------------------------------------------- |                     |                     |         |
| All Challengers:                                               |                     |                     |         |
| ----------------------------------------------------------     |                     |                     |         |
|                                                                | CTO (Architecture)  | Evidence: ████████  | [ Add ] |
|                                                                | CFO (Cost/ROI)      | Evidence: ██████    | [ Add ] |
|                                                                | Compliance/Risk     | Evidence: █████████ | [ Add ] |
|                                                                | Ops Lead (optional) | Evidence: ████      | [ Add ] |
|                                                                | Competitive Analyst | Evidence: ███████   | [ Add ] |
| ----------------------------------------------------------     |                     |                     |         |
|                                                                |                     |                     |         |
| [ Start Simulation → ]                                         |                     |                     |         |

---

```

### **Notes:**
- Evidence bar shows how many facts/questions were generated
- User can toggle challengers on/off
- System preselects strongest 2–3 challengers

---

## **5.4 Screen: Demo Room (Primary Simulation Environment)**
### **Purpose:**
The core experience — SC delivers slides and responds to challenger questions.

### **Wireframe:**
```

---

| Slide 3 / 12                         < Slide Title >                  |                            |   |
| --------------------------------------------------------------------- | -------------------------- | - |
| [ CTO Avatar ]                [ Current Slide Content ]               |                            |   |
| (speech bubble if active)                                             |                            |   |
|                                                                       |                            |   |
|                                                                       |                            |   |
| [ CFO Avatar ]                                                        |                            |   |
| (speech bubble if active)                                             |                            |   |
|                                                                       |                            |   |
| [ Compliance Avatar ]                                                 |                            |   |
| (speech bubble if active)                                             |                            |   |
| --------------------------------------------------------------------- |                            |   |
| Your Response:                                                        |                            |   |
| ---------------------------------------------------------------       |                            |   |
|                                                                       | [ Type your answer here… ] |   |
| ---------------------------------------------------------------       |                            |   |
| [ Submit Answer ]                                                     |                            |   |

---

```

### **Notes:**
- Avatars arranged around the slide (1–4 depending on selection)
- Speech bubbles appear dynamically when challengers fire
- Slide viewer supports:
  - Previous / Next buttons
  - Keyboard arrows
  - Slide index indicator

---

## **5.5 Screen: Session Summary / Score Report**
### **Purpose:**
Provide a polished, client-ready evaluation report.

### **Wireframe:**
```

---

| Session Summary                                                |            |           |                 |           |   |
| -------------------------------------------------------------- | ---------- | --------- | --------------- | --------- | - |
| Overall Readiness Score:    78 / 100                           |            |           |                 |           |   |
| (Gauge visualization)                                          |            |           |                 |           |   |
| -------------------------------------------------------------- |            |           |                 |           |   |
| Challenger Performance                                         |            |           |                 |           |   |
| ----------------------------------------------------------     |            |           |                 |           |   |
|                                                                | CTO        | Score: 74 | Strengths: X, Y | Gaps: A   |   |
|                                                                | CFO        | Score: 81 | Strengths: X    | Gaps: B,C |   |
|                                                                | Compliance | Score: 69 | Strengths: Y    | Gaps: D   |   |
| ----------------------------------------------------------     |            |           |                 |           |   |
| -------------------------------------------------------------- |            |           |                 |           |   |
| Slide-by-Slide Breakdown                                       |            |           |                 |           |   |
| Slide 1: 82   Slide 2: 74   Slide 3: 90  Slide 4: 63           |            |           |                 |           |   |
| -------------------------------------------------------------- |            |           |                 |           |   |
| Top Opportunities                                              |            |           |                 |           |   |
| • Tighten architecture clarity                                 |            |           |                 |           |   |
| • Strengthen ROI narrative                                     |            |           |                 |           |   |
| • Address compliance nuances earlier                           |            |           |                 |           |   |
| -------------------------------------------------------------- |            |           |                 |           |   |
| [ Export JSON ]   [ Exit ]                                     |            |           |                 |           |   |

---

```

### **Notes:**
- Clean, executive-friendly format
- Could be exported as JSON (PDF export in V2)

---

## **5.6 Visual Identity & Branding**
### The app must feel **productized**, not prototype.
- Typography: Inter / Roboto / Source Sans
- Colors: cool greys + accent color (blue or teal)
- Avatar shapes: circular with soft shadows
- Buttons: filled primary, outlined secondary
- Motion: subtle fade + slide transitions

---

## **5.7 Responsiveness & Layout Handling**
- Desktop-first experience
- Tablet compatible
- Mobile layout minimized or read-only (future)

---

This screen architecture now positions the MVP as something you could **demo, sell, or productize**, not a prototype.

### **5.1 Flow**
1. Upload deck  
2. Processing screen (deck ingestion + research + challenge-set precomputation)  
3. **Challenger selection screen**  
4. Enter Demo Room  

On the challenger selection screen:
- Show a list/grid of all configured challengers (from `challengers.json`)
- For each challenger, display:
  - name, role, domain tags
  - a short description
  - an **"evidence richness" indicator** derived from how many questions/facts were generated for that challenger during precomputation
- Default recommendation:
  - Auto-select the 2–3 challengers with the strongest evidence coverage (most relevant slides + facts)
- Allow the user to:
  - toggle challengers on/off for this session
  - optionally change the number of active challengers
- Only the selected challengers will:
  - fire questions in the Demo Room
  - appear as avatars around the slide

### **5.2 Slide Viewer**
- Next/Prev controls  
- Display title + text  
- Track `current_slide_index`

### **5.3 Challenger Avatars (User-Selected)**
- In the Demo Room, render avatars only for the **user-selected challengers** from the challenger selection screen
- Layout (example for 3 active challengers):
  - CTO (top-left)
  - CFO (top-right)
  - Compliance (bottom-right)
- If fewer/more challengers are selected, adapt layout responsively (e.g., 1–4 avatar positions)
- Each avatar area includes:
  - Name/role label
  - Speech bubble area (hidden when silent)
- Avatar art is loaded from:
  - challenger-specific generated avatars (if available)
  - otherwise from static default placeholders

### **5.4 Challenge Display Logic**
On slide change:
- Backend returns 0–2 challenges  
- Randomized with trigger probabilities  
- If triggered → show speech bubble

### **5.5 Response Input**
Single text area:
```

[ Type your answer here... ] [Submit]

````

### **5.6 Tests**
- Navigation tests
- Speech bubble mapping tests
