# 🧮 **Phase 6 — Scoring & Evaluation Engine**

### **6.1 Encoding**
- Reuse embedding model  
- Encode SC answer + ideal answer

### **6.2 Similarity + Heuristics**
Compute:
- cosine similarity  
- completeness (keyword coverage)  
- clarity (length + relevance)  

Apply rubric weights → score 0–100.

### **6.3 Persistence**
Store interactions:
```json
{
  "slide_index": 1,
  "challenger_id": "cto",
  "question_id": "q123",
  "user_answer": "...",
  "score": 78
}
````

### **6.4 UI Feedback**

MVP:
Show a small badge next to the question:

* Good
* Okay
* Weak

### **6.5 Tests**

* Identical answers → high score
* Non-relevant answers → low score
