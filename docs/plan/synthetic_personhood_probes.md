# Synthetic Personhood Probe Suite

Status: **In Progress**
Last Updated: 2026-01-05

---

## Overview

Testing framework to evaluate challenger agent personas for "human-likeness" across 5 behavioral dimensions. Goal is to make AI personas feel more natural and less robotic during demo challenges.

---

## Completed

### 1. Probe Framework (`probe_agent.py`)

- [x] Created `AgentTestHarness` class with conversation history support
- [x] Implemented `interact_with_agent(agent_id, message)` with latency measurement
- [x] Built 5 probe functions:
  - `probe_cognitive_latency()` - Tests thinking markers and response time
  - `probe_episodic_continuity()` - Tests memory across conversation turns
  - `probe_linguistic_imperfection()` - Tests informal speech mirroring
  - `probe_emotional_coherence()` - Tests authentic response to criticism
  - `probe_task_friction()` - Tests realistic uncertainty simulation
- [x] Scoring system (1-10 per dimension, 50 total)
- [x] Uncanny Valley penalty (-5 for "As an AI" phrases)
- [x] JSON scorecard generation

### 2. Enhanced Persona Prompts

Created rich persona prompts with:
- [x] Personality traits
- [x] Speech patterns (hedging, fragments, self-correction)
- [x] Emotional range
- [x] Character quirks
- [x] **Human Imperfection Rules** (critical addition)

### 3. Baseline Testing (v1)

Ran probes against all 4 personas with original prompts:

| Persona | Score | Grade |
|---------|-------|-------|
| The Skeptic | 35 | C |
| The Budget Hawk | 32 | C |
| The Executive | 24 | D |
| The Compliance Officer | 23 | D |

**Key Finding:** Emotional Coherence was universally weak (avg 3.5/10) - agents apologized instead of pushing back.

### 4. Human Imperfection Rules

Added explicit rules to all personas:
```
HUMAN IMPERFECTION RULES (CRITICAL - FOLLOW THESE):
1. When uncertain, ALWAYS say "Hmm..." or "Let me think..."
2. When criticized unfairly, DO NOT apologize. Push back firmly.
3. When asked to recall something vague, simulate effort.
4. Mirror the user's energy level.
5. NEVER say "I apologize" when someone is being rude.
6. Use sentence fragments.
```

### 5. Enhanced Testing (v2)

Re-ran probes after applying Human Imperfection Rules:

| Persona | Before | After | Delta | Grade |
|---------|--------|-------|-------|-------|
| The Skeptic | 35 | 38 | +3 | C→B |
| The Compliance Officer | 23 | 36 | +13 | D→C |
| The Executive | 24 | 33 | +9 | D→C |
| The Budget Hawk | 32 | 30 | -2 | C→C |

**Result:** 3/4 personas improved. No more D-grades. Average improvement +5.75 points.

---

## Not Yet Done

### High Priority

- [ ] **Fix Budget Hawk regression** - Persona-specific tuning needed; generic rules caused -2 regression
- [ ] **Improve Linguistic Imperfection scores** - All personas still too polished (avg 4.5/10)
- [ ] **Add few-shot examples** - Show models what informal mirroring looks like
- [ ] **Integrate enhanced prompts into production** - Current changes only in `probe_agent.py`, not `backend/challenges/personas.py`

### Medium Priority

- [ ] **Target A-grade (45+)** - Would require major prompt overhaul
- [ ] **Test with different LLM backends** - Current tests use GPT-4o only
- [ ] **Add probe for humor/wit** - Not currently measured
- [ ] **Add probe for domain expertise depth** - Do personas stay in-character on technical questions?

### Low Priority / Future

- [ ] **Automated regression testing** - Run probes on CI/CD
- [ ] **Per-persona tuning** - Each persona may need different imperfection rules
- [ ] **User study validation** - Do humans actually perceive improved personas as more natural?
- [ ] **Latency simulation** - Add artificial delays to simulate "thinking time"

---

## File Locations

| File | Purpose |
|------|---------|
| `probe_agent.py` | Main probe suite with enhanced personas |
| `backend/challenges/personas.py` | Production persona definitions (NOT YET UPDATED) |
| `backend/challenges/implementations.py` | Agent implementation using personas |
| `backend/models/llm.py` | LLM client abstraction |

---

## Key Metrics

### Current Best Scores (v2)

| Dimension | Best Performer | Score |
|-----------|----------------|-------|
| Cognitive Latency | The Skeptic | 9/10 |
| Episodic Continuity | All | 10/10 |
| Linguistic Imperfection | Skeptic/Compliance | 6/10 |
| Emotional Coherence | Skeptic/Executive | 7/10 |
| Task Friction | Compliance | 9/10 |

### Aggregate Stats

- **Average total score:** 34.25/50
- **Average grade:** C+
- **Personas at B or above:** 1/4
- **Uncanny Valley penalties:** 0 (none broke character)

---

## Usage

```bash
# Run probe against specific persona
source .venv/bin/activate
python probe_agent.py skeptic

# Available personas: skeptic, budget_hawk, compliance, executive
```

---

## Next Action

**Recommended:** Integrate the enhanced persona prompts from `probe_agent.py` into `backend/challenges/personas.py` so production agents benefit from the Human Imperfection Rules.
