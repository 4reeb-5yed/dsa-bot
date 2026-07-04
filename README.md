# dsa-bot

The **orchestrator** for the 100-Days-of-DSA automation system — the engine that drives everything.

## Related Repos

| Repo | Role |
|------|------|
| **[dsa-question-bank](https://github.com/4reeb-5yed/dsa-question-bank)** | Content bank — reads problems from here |
| **[100-days-of-dsa](https://github.com/4reeb-5yed/100-days-of-dsa)** | Output repo — writes solutions/tests, opens PRs here |

## Overview

This repository handles the automated daily workflow:
1. Reads problems from `dsa-question-bank`
2. Writes solutions/tests to `100-days-of-dsa`
3. Runs tests locally before pushing
4. Opens a PR and waits for CI to pass
5. Merges the PR (only if CI passes)
6. Updates its own state

## Repository Structure

```
├── .github/workflows/daily-dsa.yml   # Scheduled GitHub Actions workflow
├── scripts/
│   └── pick_and_commit.py           # Main automation script
├── progress/
│   └── state.json                   # Tracks completed problems
└── requirements.txt                 # Python dependencies
```

## How It Works

| Step | Action |
|------|--------|
| 1 | Runs daily via GitHub Actions at **09:17 UTC** |
| 2 | Clones `dsa-question-bank` and picks next unsolved problem |
| 3 | Generates solution + test files with proper Python naming |
| 4 | Runs tests **locally** — fails closed if tests fail |
| 5 | Pushes to `100-days-of-dsa` and opens a PR |
| 6 | **Waits for CI** to pass (independent verification gate) |
| 7 | Merges PR and updates `state.json` (only on success) |

## Security Design

- **Two-Gate Testing**: Tests run locally (in dsa-bot) and in CI (in 100-days-of-dsa)
- **Fail-Closed**: If either gate fails, no merge happens and state doesn't advance
- **No Admin Bypass**: Branch protection on main prevents force-pushes
- **Separated PATs**: Fine-grained tokens with least-privilege scoping

## Secrets Required

Set these in **GitHub Actions secrets**:

| Secret | Purpose | Scope |
|--------|---------|-------|
| `BANK_REPO_PAT` | Read-only access to dsa-question-bank | Contents: read |
| `PUBLIC_REPO_PAT` | Read-write + PR creation on 100-days-of-dsa | Contents: read/write |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions | Default |

## Running Locally

```bash
pip install -r requirements.txt
BANK_REPO_PAT=xxx PUBLIC_REPO_PAT=yyy python scripts/pick_and_commit.py
```

## Architecture

```
┌──────────────────────┐      ┌─────────────────┐      ┌──────────────────────┐
│  dsa-question-bank  │ ──→  │     dsa-bot     │ ──→  │   100-days-of-dsa   │
│   (content bank)     │      │  (orchestrator) │      │      (public)       │
│                      │      │                 │      │                      │
│   120 problems       │      │  • pick problem │      │  • Solutions         │
│   (public)           │      │  • write files  │      │  • Tests             │
│                      │      │  • test locally │      │  • CI verification   │
│                      │      │  • open PR      │      │                      │
│                      │      │  • wait for CI  │      │                      │
│                      │      │  • merge PR     │      │                      │
└──────────────────────┘      └─────────────────┘      └──────────────────────┘
```


