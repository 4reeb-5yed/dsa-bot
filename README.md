# dsa-bot

Private orchestrator for the 100-Days-of-DSA automation system.

This repository contains:
- `scripts/pick_and_commit.py` - The main automation script
- `progress/state.json` - Tracks which problems have been completed
- `.github/workflows/daily-dsa.yml` - GitHub Actions workflow (schedule + manual trigger)

## How It Works

1. Runs daily via GitHub Actions at 09:17 UTC
2. Reads the question bank from `dsa-question-bank` (private)
3. Picks the next unsolved problem
4. Writes solution and test files to `100-days-of-dsa` (public)
5. Opens a PR, waits for CI, and merges
6. Updates its own `state.json`

## Secrets Required

Set these in GitHub Actions secrets:
- `BANK_REPO_PAT` - Fine-grained PAT for dsa-question-bank (read-only)
- `PUBLIC_REPO_PAT` - Fine-grained PAT for 100-days-of-dsa (read-write + PR)
- `GITHUB_TOKEN` - Default GitHub token (provided automatically)
