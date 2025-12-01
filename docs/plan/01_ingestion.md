# 🧩 **Phase 1 — Deck Ingestion & Slide Mapping**

### **1.1 Upload Handler**

* Endpoint: `POST /upload-deck`
* Save raw file → `data/decks/{session_id}/`
* Extract **Deck Metadata**:
  * Author
  * Creation/Modification Date
  * Total Slide Count

### **1.2 Slide Extraction (Complex PPT/PPTX-Aware)**

* Support **both**:

  * PDF exports of decks
  * Native `.ppt` / `.pptx` files
* For PPT/PPTX, extraction must handle complex layouts:

  * Multiple text boxes and shapes
  * Multi-column layouts
  * Tables and charts with labels
  * Grouped shapes
  * Speaker notes
* Implement a layered strategy:

  * Primary: use `python-pptx` to iterate shapes and text frames in a sensible reading order
  * Extract:

    * visible text from text frames
    * table cell text
    * chart titles / axis labels (where accessible)
    * speaker notes as a separate field
  * Optional enhancement: if layout is too complex or text extraction is incomplete, allow a **fallback conversion to PDF** (e.g., via LibreOffice/office-to-pdf) and run the PDF extractor on that page as a backup signal.
  * **OCR / Vision Support**:
    * Detect slides with low text density or high image content (screenshots, diagrams).
    * Use a vision model (e.g., GPT-4o-mini or Tesseract) or OCR service to extract text from these images.
    * Merge OCR text with any native text found.
* Maintain for each slide:

  * slide index
  * raw concatenated text (for chunking)
  * structured elements (optional future use): list of text blocks with approximate order/region
  * notes text
* Output JSON structure per slide:

```json
{
  "index": 0,
  "title": "Slide Title",
  "raw_text": "Slide content text from all text boxes/tables/labels",
  "notes": "Optional speaker notes"
}
```

### **1.3 Chunking (for Embeddings & Retrieval)**

* Treat each chunk as a **semantic retrieval unit**
* Split based on:

  * bullets
  * headings
  * sentence boundaries
* Enforce max token/char size per chunk to keep embedding quality high
* Preserve links back to:

  * slide index
  * slide title
  * original text span (for later highlighting in the UI)
* Explicit goal: enable **high-quality similarity search** over deck content when challengers generate questions and when ideal answers are built.

### **1.4 Slide Tagging**

* Tag categories:

  * `architecture`, `cost`, `security`, `integration`,
    `workflow`, `value`, `compliance`
* Lightweight keyword-based tagging

### **1.5 Embedding + Vector Store**

* Generate embeddings for each chunk using the shared embedding model
* Store per chunk:

```json
{
  "chunk_id": "uuid",
  "slide_index": 0,
  "text": "chunk text",
  "tags": ["architecture"],
  "embedding": [...]
}
```

* Initialize a per-session vector index (Chroma/FAISS)
* Expose a retrieval API:

  * `get_nearest_chunks(query_text, k)` → list of chunk objects
* This retrieval layer is **mandatory** input for:

  * research grounding (linking deck claims to external facts)
  * challenger question generation
  * ideal answer generation

### **1.6 Tests**

* PDF extraction test
* PPTX extraction test
* Chunk size test
* Tag accuracy test
