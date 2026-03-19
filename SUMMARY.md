# Summary: Wire Claude as primary LLM provider in demoGauntlet backend

## What was done
Added a `create_llm_client()` factory function to `backend/models/llm.py` that selects
Anthropic (`claude-sonnet-4-5`) when `ANTHROPIC_API_KEY` is set, falling back to
OpenAI (`gpt-4o`) when `OPENAI_API_KEY` is set. Updated the four call sites that
hardcoded `OpenAIClient` to use this factory.

## Key findings / Output
- `AnthropicClient` and `ANTHROPIC_API_KEY` config were **already implemented** — the gap was only in the four router/orchestrator files that still instantiated `OpenAIClient` directly.
- `anthropic>=0.40.0` was **already in `requirements.txt`** — no dependency changes needed.
- 5 files modified: `backend/models/llm.py` (+factory), `challenges/router.py`, `research/router.py`, `probes/router.py`, `orchestrator/loop.py`
- All files pass `py_compile`; public API surface verified unchanged.

## Actions needed
Set `ANTHROPIC_API_KEY` in `.env` or deployment environment. No other configuration
required — `requirements.txt` already includes `anthropic>=0.40.0`.
