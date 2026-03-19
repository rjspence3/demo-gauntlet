# Migration Notes: OpenAI → Claude (Anthropic)

## What Changed

### `backend/models/llm.py`
- **New function: `create_llm_client()`** — factory that returns `AnthropicClient` when
  `ANTHROPIC_API_KEY` is set, falls back to `OpenAIClient` when `OPENAI_API_KEY` is set,
  raises `ValueError` if neither is provided.
- No changes to existing classes (`LLMClient`, `AnthropicClient`, `OpenAIClient`, `MockLLM`).
  Both clients were already implemented; this migration wires Anthropic as the default.

### `backend/challenges/router.py`
- `get_llm()`: replaced `OpenAIClient(api_key=config.OPENAI_API_KEY)` with `create_llm_client()`.
- Error message updated to mention `ANTHROPIC_API_KEY` as the preferred key.

### `backend/research/router.py`
- `get_agent()`: replaced `OpenAIClient(...)` with `create_llm_client()`.
- Error message updated similarly.

### `backend/probes/router.py`
- Replaced `OpenAIClient(api_key=config.OPENAI_API_KEY)` with `create_llm_client()`.
- Guard condition changed from `if not config.OPENAI_API_KEY` to checking both keys.

### `backend/orchestrator/loop.py`
- `_setup_llm()`: now checks `ANTHROPIC_API_KEY` first → `AnthropicClient("claude-sonnet-4-5")`,
  then `OPENAI_API_KEY` → `OpenAIClient("gpt-4o")`, then `MockLLM` (graceful fallback preserved).

## Dependencies

`requirements.txt` already contains both providers:
```
anthropic>=0.40.0   # primary — Claude claude-sonnet-4-5
openai==1.61.0      # fallback — gpt-4o
```
No changes to `requirements.txt` or `pyproject.toml` are needed.

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Preferred** | Enables Claude as primary provider |
| `OPENAI_API_KEY` | Fallback only | Used if `ANTHROPIC_API_KEY` is not set |

Both are already defined in `backend/config.py` as optional fields.

## Default Models

| Provider | Default Model | Override |
|---|---|---|
| Anthropic | `claude-sonnet-4-5` | Pass `anthropic_model=` to `create_llm_client()` |
| OpenAI | `gpt-4o` | Pass `openai_model=` to `create_llm_client()` |

## How to Test

### Local dev with Claude:
```bash
# Set key in .env or shell
export ANTHROPIC_API_KEY=sk-ant-...

# Start backend
uvicorn backend.main:app --reload

# Hit any challenge/research endpoint — logs will show AnthropicClient being used
```

### Verify provider selection at runtime:
```python
from backend.models.llm import create_llm_client
client = create_llm_client(anthropic_api_key="sk-ant-...")
print(type(client).__name__)  # → AnthropicClient
```

### Force OpenAI fallback (unset Anthropic key):
```bash
unset ANTHROPIC_API_KEY
export OPENAI_API_KEY=sk-...
# Restart server → OpenAIClient will be used
```

### Existing tests are unaffected:
- All tests use `MockLLM` or `MagicMock` — no real API calls.
- `backend/probes/harness.py` already hardcodes `AnthropicClient` directly (unchanged).
- `backend/tests/test_llm.py` tests `OpenAIClient` with a fake key (still valid).

## Unchanged Behavior

- All public method signatures on `LLMClient`, `AnthropicClient`, and `OpenAIClient` are identical.
- `MockLLM` is unchanged.
- Retry logic (tenacity) is unchanged on both clients.
- The `AnthropicClient` already handled markdown stripping from structured responses;
  this behavior is preserved.
