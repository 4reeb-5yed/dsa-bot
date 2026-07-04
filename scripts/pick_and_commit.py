#!/usr/bin/env python3
"""
DSA Bot - Pick and Commit Script
Reads from dsa-question-bank, creates solution/test files in 100-days-of-dsa,
opens a PR, merges it, then updates own progress/state.json.
"""

import json
import sys
import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, date

BANK_REPO_PAT = os.environ.get("BANK_REPO_PAT", "")
PUBLIC_REPO_PAT = os.environ.get("PUBLIC_REPO_PAT", "")
REPO_OWNER = os.environ.get("REPO_OWNER", "4reeb-5yed")

BANK_REPO = f"https://x-access-token:{BANK_REPO_PAT}@github.com/{REPO_OWNER}/dsa-question-bank.git"
PUBLIC_REPO = f"https://x-access-token:{PUBLIC_REPO_PAT}@github.com/{REPO_OWNER}/100-days-of-dsa.git"
DSA_BOT_REPO = f"https://x-access-token:{os.environ.get('GITHUB_TOKEN', '')}@github.com/{REPO_OWNER}/dsa-bot.git"


def get_today_utc():
    return date.today().isoformat()


def load_state(state_path):
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return {"next_index": 0, "solved_ids": [], "last_run_date": None}


def save_state(state_path, state):
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


def run_cmd(cmd, cwd=None, env=None, check=True):
    """Run a command and return stdout."""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        print(f"ERROR: Command failed: {cmd}", file=sys.stderr)
        print(f"stdout: {result.stdout}", file=sys.stderr)
        print(f"stderr: {result.stderr}", file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result.stdout.strip()


def main():
    print("=" * 50)
    print("DSA Bot - Starting daily run")
    print("=" * 50)

    # Determine script directory for state file
    script_dir = Path(__file__).parent.resolve()
    repo_dir = script_dir.parent
    state_file = repo_dir / "progress" / "state.json"

    # Load current state
    state = load_state(state_file)
    print(f"Current state: {state}")

    today = get_today_utc()
    print(f"Today (UTC): {today}")

    # Guard: already ran today
    if state.get("last_run_date") == today:
        print(f"Already ran today ({today}). Exiting.")
        sys.exit(0)

    # Clone bank repo
    print("\nCloning question bank...")
    bank_tmp = tempfile.mkdtemp(prefix="bank_")
    try:
        run_cmd(f"git clone {BANK_REPO} {bank_tmp}")
        bank_path = Path(bank_tmp) / "problems" / "bank.json"
        with open(bank_path) as f:
            bank = json.load(f)
        print(f"Loaded {len(bank)} problems from bank")
    finally:
        pass  # Keep temp dir for now

    # Guard: bank exhausted
    if state["next_index"] >= len(bank):
        print("Bank exhausted. No more problems to solve.")
        sys.exit(0)

    # Pick entry
    entry = bank[state["next_index"]]
    day = state["next_index"] + 1
    day_str = f"{day:03d}"
    slug = entry["slug"]
    module_slug = slug.replace("-", "_")  # hyphens invalid in Python identifiers
    title = entry["title"]
    topic = entry["topic"]
    difficulty = entry["difficulty"]
    solution_code = entry["solution_code"]
    test_code = entry["test_code"]

    print(f"\nPicking problem {day}: {title} ({topic}, {difficulty})")

    # Clone public repo
    print("\nCloning public repo...")
    public_tmp = tempfile.mkdtemp(prefix="public_")
    try:
        run_cmd(f"git clone {PUBLIC_REPO} {public_tmp}")

        # Write solution file (use underscores for Python module name)
        sol_dir = Path(public_tmp) / "solutions"
        sol_dir.mkdir(exist_ok=True)
        sol_file = sol_dir / f"day_{day_str}_{module_slug}.py"
        with open(sol_file, 'w') as f:
            f.write(solution_code)
        print(f"Wrote {sol_file}")

        # Write test file - need to fix the import line to use underscores
        test_dir = Path(public_tmp) / "tests"
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / f"test_day_{day_str}_{module_slug}.py"
        # Fix import in test_code: replace hyphens with underscores in the import line
        fixed_test_code = test_code.replace(f"day_{day_str}_{slug}", f"day_{day_str}_{module_slug}")
        with open(test_file, 'w') as f:
            f.write(fixed_test_code)
        print(f"Wrote {test_file}")

        # Update README progress table
        readme_path = Path(public_tmp) / "README.md"
        if readme_path.exists():
            with open(readme_path) as f:
                readme_content = f.read()
            # Insert row before PROGRESS_TABLE_END
            new_row = f"| {day_str} | {title} | {topic} | {difficulty} | {today} |\n"
            readme_content = readme_content.replace(
                "<!-- PROGRESS_TABLE_END -->",
                new_row + "<!-- PROGRESS_TABLE_END -->"
            )
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            print("Updated README progress table")

        # Test locally before pushing
        print("\nRunning tests locally...")
        env = os.environ.copy()
        env["PYTHONPATH"] = public_tmp
        test_result = subprocess.run(
            f"cd {public_tmp} && python -m pytest tests/test_day_{day_str}_{module_slug}.py -v",
            shell=True,
            capture_output=True,
            text=True,
            env=env
        )
        print(test_result.stdout)
        if test_result.returncode != 0:
            print("TESTS FAILED - not pushing anything", file=sys.stderr)
            print(test_result.stderr, file=sys.stderr)
            sys.exit(1)

        print("Tests passed!")

        # Commit and push to public repo
        print("\nPushing to public repo...")
        branch_name = f"day-{day_str}-{slug}"
        run_cmd(f"git checkout -b {branch_name}", cwd=public_tmp)
        run_cmd(f"git add solutions/ tests/ README.md", cwd=public_tmp)
        run_cmd(
            f'git -c user.name="dsa-bot" -c user.email="dsa-bot@users.noreply.github.com" '
            f'commit -m "Day {day_str}: {title} ({topic}, {difficulty})"',
            cwd=public_tmp
        )
        run_cmd(f"git push origin {branch_name}", cwd=public_tmp)

        # Create and merge PR using gh
        print("\nCreating PR...")
        pr_body = f"Automated daily DSA solution. Verified passing before merge.\n\nProblem: {title}\nTopic: {topic}\nDifficulty: {difficulty}"
        
        run_cmd(
            f'gh pr create --repo {REPO_OWNER}/100-days-of-dsa '
            f'--title "Day {day_str}: {title}" '
            f'--body "{pr_body}" '
            f'--base main --head {branch_name}',
            env={**os.environ, "GH_TOKEN": PUBLIC_REPO_PAT}
        )

        print("Merging PR...")
        run_cmd(
            f'gh pr merge --repo {REPO_OWNER}/100-days-of-dsa '
            f'--squash --delete-branch --admin {branch_name}',
            env={**os.environ, "GH_TOKEN": PUBLIC_REPO_PAT}
        )

        print(f"Successfully merged Day {day_str}: {title}")

    finally:
        shutil.rmtree(public_tmp, ignore_errors=True)
        shutil.rmtree(bank_tmp, ignore_errors=True)

    # Update own state (only after successful merge)
    print("\nUpdating dsa-bot state...")
    state["next_index"] += 1
    state["solved_ids"].append(entry["id"])
    state["last_run_date"] = today
    save_state(state_file, state)

    # Push state update to dsa-bot repo
    print("Pushing state update...")
    dsa_bot_tmp = tempfile.mkdtemp(prefix="dsa_bot_")
    try:
        run_cmd(f"git clone {DSA_BOT_REPO} {dsa_bot_tmp}")
        
        # Copy state file
        dst_state = Path(dsa_bot_tmp) / "progress" / "state.json"
        dst_state.parent.mkdir(exist_ok=True)
        shutil.copy2(state_file, dst_state)
        
        run_cmd(f"git add progress/state.json", cwd=dsa_bot_tmp)
        run_cmd(
            f'git -c user.name="dsa-bot" -c user.email="dsa-bot@users.noreply.github.com" '
            f'commit -m "Update state: completed Day {day_str}"',
            cwd=dsa_bot_tmp
        )
        run_cmd("git push origin main", cwd=dsa_bot_tmp)
        print("State pushed to dsa-bot")
    finally:
        shutil.rmtree(dsa_bot_tmp, ignore_errors=True)

    print("\n" + "=" * 50)
    print(f"SUCCESS: Day {day_str} completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
