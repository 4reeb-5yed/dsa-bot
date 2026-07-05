#!/usr/bin/env python3
"""
Test that shell injection is properly prevented in git commit messages.
Issue 2: Shell injection via bank-sourced content.

This test ACTUALLY EXECUTES the code path being tested.
It creates a real git repo, calls the actual run_cmd_list function,
and verifies:
  (a) no injected side effect occurred (sentinel file not created)
  (b) the commit message contains the malicious content as literal text
"""
import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from pick_and_commit import run_cmd_list


def test_git_commit_message_injection():
    """
    Test that malicious bank content in commit message doesn't cause shell injection.
    Uses the ACTUAL run_cmd_list function from pick_and_commit.py.
    """
    # Malicious bank entry content
    malicious_title = 'Two Sum"; touch /tmp/pwned_injection_test; echo "'
    malicious_topic = 'arrays'
    malicious_difficulty = 'easy'
    
    # Create a temp git repo for testing
    test_dir = tempfile.mkdtemp(prefix="injection_test_")
    repo_dir = os.path.join(test_dir, "repo")
    os.makedirs(repo_dir)
    
    sentinel_file = Path("/tmp/pwned_injection_test")
    # Clean up any previous sentinel
    if sentinel_file.exists():
        sentinel_file.unlink()
    
    print("=" * 70)
    print("SHELL INJECTION TEST")
    print("=" * 70)
    print(f"Test directory: {test_dir}")
    print(f"Malicious title: {repr(malicious_title)}")
    print()
    
    try:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_dir, capture_output=True, check=True)
        
        # Create a dummy file
        dummy_file = os.path.join(repo_dir, "test.txt")
        with open(dummy_file, "w") as f:
            f.write("test content")
        
        # Stage the file
        subprocess.run(["git", "add", "test.txt"], cwd=repo_dir, capture_output=True, check=True)
        
        # Build the commit message exactly as pick_and_commit.py does
        day_str = "001"
        commit_msg = f"Day {day_str}: {malicious_title} ({malicious_topic}, {malicious_difficulty})"
        
        print(f"Commit message: {repr(commit_msg)}")
        print()
        
        # Call the ACTUAL run_cmd_list function from pick_and_commit.py
        # This is the same function and arguments used in the fixed code
        run_cmd_list(
            ["git", "-c", "user.name=4reeb-5yed",
             "-c", "user.email=284557362+4reeb-5yed@users.noreply.github.com",
             "commit", "-m", commit_msg],
            cwd=repo_dir
        )
        
        print("✅ Git commit succeeded (no shell injection)")
        print()
        
        # Check if sentinel file was created (proof of injection)
        if sentinel_file.exists():
            print("❌ FAILURE: Sentinel file was created! Shell injection occurred!")
            return 1
        else:
            print("✅ (a) No sentinel file created - no injected side effect")
        
        # Verify the commit message contains the malicious content as literal text
        result = subprocess.run(
            ["git", "log", "-1", "--format=%B"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        actual_msg = result.stdout.strip()
        print()
        print(f"Actual commit message: {repr(actual_msg)}")
        
        if malicious_title in actual_msg:
            print("✅ (b) Malicious content preserved as literal text in commit")
        else:
            print("❌ FAILURE: Malicious content was NOT preserved in commit message!")
            print(f"   Expected to find: {repr(malicious_title)}")
            print(f"   In: {repr(actual_msg)}")
            return 1
        
        print()
        print("=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70)
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILURE: Git command failed with exit code {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return 1
        
    finally:
        # Clean up
        shutil.rmtree(test_dir, ignore_errors=True)
        if sentinel_file.exists():
            sentinel_file.unlink()


def test_old_vulnerable_approach():
    """
    For comparison: show what happens with the VULNERABLE approach.
    This demonstrates why the old code was exploitable.
    """
    print()
    print("=" * 70)
    print("COMPARISON: What the OLD vulnerable code would produce")
    print("=" * 70)
    
    malicious_title = 'Two Sum"; touch /tmp/pwned_injection_test; echo "'
    day_str = "001"
    
    # OLD vulnerable approach (shell=True with nested quoting)
    old_vulnerable_cmd = f'git commit -m "Day {day_str}: {malicious_title} (arrays, easy)"'
    print(f"Old vulnerable command:\n  {old_vulnerable_cmd}")
    print()
    print("When run through shell=True, this becomes:")
    print("  git commit -m \"Day 001: Two Sum\"")
    print("  touch /tmp/pwned_injection_test")
    print("  echo \" (arrays, easy)\"")
    print()
    print("The double quote in the title closes the -m string early,")
    print("allowing injection of arbitrary commands.")
    print("=" * 70)


if __name__ == '__main__':
    result = test_git_commit_message_injection()
    test_old_vulnerable_approach()
    sys.exit(result)
