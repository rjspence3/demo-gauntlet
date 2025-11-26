# Rules.md — Non-Negotiable Rules

## 🔒 Safety & Permissions

- Auto-execute only read-only commands (`git status`, `ls`). Never auto-execute `git add/commit`, `rm`, destructive DB ops, or network-mutating scripts.
    
- Never print, store, or commit secrets/tokens/PII.
    
- Do not modify: `/migrations/`, `/secrets/`, `/legacy/` unless task explicitly grants it with plan + tests.
    

---

## 🔍 Stage Awareness

- All rules must be applied **inside the stage lifecycle defined in `claude.md`** (`Init → Ask → Design → Plan → Tests → Code → Explain`).
    
- A **review stage** (`Review → Summarize → Approve`) follows `Code → Explain`.
    
- A rule violation blocks stage progression. Claude must stop and escalate before continuing.
    
- All review output must follow the **JSON artifact contract** (see "Code Review Output").
    
- Any **critical or high** issue halts progression until fixed or waived in `design.md`.
    

---

## 🔎 Planning & Workflow

- **Plan first:** produce a numbered roadmap of files/functions to touch + components to reuse.
    
- **Tests before code:** write or extend tests first; add regression tests for any bug fixed.
    
- **Code minimal:** implement the minimum needed to pass tests.
    
- **Explain decisions:** record risks, alternatives, and contract changes after coding.
    
- **Evidence discipline:** every claim or fix suggestion must cite `file:line` or `file:start-end`.
    
- Prefer **small diffs** that neutralize the risk ("minimal, high-impact change").
    
- For inconclusive data (missing config/tests/logs), output an `"inconclusive"` issue describing what’s needed.
    

---

## 🥺 TDD & CI Gates

- Local gates (must pass before proposing diff):
    
    - Lint: `make lint`
        
    - Typecheck: `make typecheck`
        
    - Unit tests (fast): `make test`
        
- Full suite + coverage ≥ **90%** on request: `make coverage`
    
- Add a **review gate:** `make review` runs static analyzers, security scanners, and coverage delta checks.
    
- Code cannot merge with:
    
    - Any **critical** or **high** unresolved issue.
        
    - Coverage <90% or missing regression IDs.
        
    - Secrets, tokens, or unredacted PII present.
        

---

## 🗞️ Contracts & Compatibility

- **Search & Reuse** existing functions/classes before creating a new one.
    
- Each function/class must include an **IO contract** in comments, in this standard format:
    
    - Inputs (name:type:required/optional)
        
    - Outputs (exact schema/return type)
        
    - Side-effects (files/DB/network)
        
    - Dependencies (components called)
        
- `design.md` contracts must map 1:1 with implemented code contracts.
    
- **Integration Check:** list impacted components; confirm IO compatibility; if mismatch → propose contract change first (with tests).
    
- Each boundary (API, queue, DB, file) must validate input/output using schemas (`pydantic`, `Zod`, etc.).
    
- When modifying contracts, list affected consumers and version impacts in `design.md`.
    
- Always enforce **timeout + retry policy** for outbound calls.
    
- RAG/data components must track **provenance** and cite their source documents.
    

---

## 💡 Pipeline Guarantees

- Each step must be runnable solo:
    
    - Reads inputs from `pipeline/<step>/inputs/` OR `get_latest("<prev_step>")`
        
    - Writes `outputs/<timestamp>/` with `manifest.json`
        
- Steps **prefer the most recent valid output** of the previous step when no explicit input is provided.
    
- Outputs must be **pure data artifacts** (no secrets; redacted if needed).
    

---

## 🖊️ PR Hygiene

- Diffs must be minimal; no drive-by refactors.
    
- PR description must include: purpose, plan vs. result, risk notes, test evidence, contract changes.
    
- Use Conventional Commits; do not mention “Claude” in commits.
    

---

## 🔊 Prompting Discipline

- Never freehand prompts.
    
- All prompts must live under `/prompts/` and follow the system: TaskBrief → PromptSpec → PromptLinter → few-shots → tests.
    
- Prompts must be linted and versioned.
    

---

## 🔏 Acceptance Criteria & Tests

- Every acceptance criterion in `design.md` must map to at least one test.
    
- Regression tests must cite the bug/criterion ID they cover.
    

---

## 🔧 Light vs Full Mode

- **Full mode (default):** All rules enforced.
    
- **Light mode (for utilities <100 LOC):** Contracts + minimal tests required, but pipeline scaffolding and coverage requirements can be skipped.
    
- Lite mode must be explicitly declared in `design.md`.
    

---

## 🔖 Code Review Output (Non-Negotiable)

Claude’s review must emit **three JSON blocks** — no prose outside them:

### (A) Per-File Findings

Minimal, evidence-backed issues with severity, risk, and fixes.

### (B) Cross-Cutting Risks & Standards

Portfolio-level risks, missing foundations, and recommended standards.

### (C) Executive Summary & Plan

Hotlist, effort breakdown, accept/revise/reject counts, and target-state checklist.

---

## 📉 Scoring & Verdicts

- **ACCEPT:** ≥4.2 average, zero criticals, tests + tracing present.
    
- **REVISE:** 3.0–4.1 or any high severity with straightforward fix.
    
- **REJECT:** <3.0 or critical security/correctness issues.
    
- Claude must print the verdict + numeric breakdown per axis.
    

---

## ⚠️ Anti-Patterns (Hard Fail)

- Secrets/tokens in code or tests.
    
- Swallowed errors (`catch {}` / `bare except`).
    
- Unbounded retries or **no timeouts** on I/O.
    
- Shared mutable singletons without locks.
    
- Ad-hoc SQL via string concat (no params).
    
- RAG results **without provenance** or eval harness.
    
- God-services that mix concerns.
    
- Tests that don’t assert outcomes / lack fixtures.
    
- Silent fallbacks that mask failures.
    

---

## 🧠 Review Axes (0–5 scale)

Claude must score each axis and cite examples:

1. Correctness & Bugs
    
2. API Contracts
    
3. Error Handling & Resilience
    
4. Security & Privacy
    
5. Performance & Complexity
    
6. Concurrency & Async
    
7. Data & RAG
    
8. Observability
    
9. Testing & Quality Gates
    
10. Architecture & SoC
    
11. Config & Deployability
    
12. Frontend
    
13. Infra/IaC
    

0 = absent, 1 = hazardous, 2 = ad-hoc, 3 = baseline, 4 = solid, 5 = exemplary.

---

## 🛠️ Stack-Specific Hooks

- **Python:** `requests` without timeout, `except Exception` without log/rethrow, async leaks, SQLAlchemy scope.
    
- **Node/TS:** unhandled promises, `any` leaks, missing Zod validation, Prisma/TypeORM N+1.
    
- **Frontend:** missing `key`, stale closures, WCAG violations, DOM XSS.
    
- **IaC/Docker:** `latest` tags, root containers, open SGs, missing healthchecks.
    

---

## 📃 Living Rules

- When a preventable mistake occurs, **add a short rule here or in `claude.md`**.
    
- Rationale and evidence go to `HISTORY.md`.
    
- If a defect should have been caught by review, add a new **rule or axis check**.