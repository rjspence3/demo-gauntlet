---
description: "Run quality gates, commit all changes, push, and open a PR. Usage: /commit-push-pr [optional context]"
---

Commit, push, and open a PR for the current changes in demoGauntlet.

**Context:** $ARGUMENTS

## Step 1: Quality gates

Backend:
```bash
source .venv/bin/activate
mypy .                # Must exit 0 — zero type errors (strict mode)
pytest --tb=short -q  # Must pass — all tests green
```

Frontend:
```bash
cd frontend && npm run lint   # Must exit 0 — zero ESLint errors
cd frontend && npm run build  # Must complete — catches broken imports
```

If any gate fails, stop and report. Do not proceed to commit.

## Step 2: Inspect changes

Run in parallel:
- `git status` — see what's staged/unstaged
- `git diff` — review what changed
- `git log --oneline -5` — match commit message style

## Step 3: Commit

Stage tracked files only:
```bash
git add -u
```

Add new source files or migrations explicitly if needed:
```bash
git add backend/migrations/versions/...  # new Alembic migration
git add backend/...                      # new source file
git add frontend/src/...                 # new frontend file
```

Do not add `.env`, `data/`, `data/chroma_db/`, or `demo_gauntlet.egg-info/`.

If on `main`, create a feature branch first:
```bash
git checkout -b feat/<short-slug>
```

Write the commit message as `type: description` (feat/fix/chore/docs/refactor/test).
Use a HEREDOC.

## Step 4: Push

```bash
git push -u origin HEAD
```

## Step 5: Open PR

```bash
gh pr create --title "..." --body "$(cat <<'EOF'
## Summary
- [bullet points of what changed]

## Test plan
- [ ] `mypy .` passes
- [ ] `pytest` passes
- [ ] `cd frontend && npm run lint && npm run build` passes
- [ ] [any manual verification at http://demo-gauntlet.test]

## Migration required?
[Yes/No — if yes: `alembic upgrade head` after merge]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
