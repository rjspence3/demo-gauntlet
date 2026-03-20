# Summary: Removed invite gate and aligned UI to dark theme

## What was done
Auto-login on mount using the existing `/auth/login-with-code` endpoint eliminates the invite gate without breaking backend auth. Three main-flow components (`DeckUpload`, `ProcessingScreen`, `ChallengerSelection`) were converted from the old light `gray-/blue-` theme to match the app shell's dark `slate-/cyan-` theme. Build and lint pass; pushed to origin; Vercel deploy triggered.

## Key findings / Output
- **Option B chosen**: backend enforces auth on all routes via `get_current_user` — purely frontend gate removal would have broken all API calls with 401s
- **Root UI issue**: DeckUpload, ProcessingScreen, ChallengerSelection were white-on-black — all three rewritten to `DGCard`-based dark theme with cyan accents
- **Invite code**: `INVITE_CODE_REDACTED` found in `deployment/backend-service-final.yaml` — also contains plaintext API keys that should be rotated

## Actions needed
- Wait ~3 min for Vercel to finish deploying, then verify at https://demo-gauntlet-ui.vercel.app
- Consider rotating the API keys exposed in `deployment/backend-service-final.yaml` (Anthropic, OpenAI, Brave)
