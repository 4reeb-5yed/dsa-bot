#!/usr/bin/env python3
"""
Test that redaction is applied to stdout/stderr in run_cmd failure.
Issue 3: PAT redaction incomplete on git-clone failure logging.
"""
import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Import the functions to test
from pick_and_commit import redact


def test_redact_function():
    """
    Verify that redact() properly masks sensitive tokens.
    """
    # Set up fake tokens for testing
    fake_token = "ghp_fake1234567890abcdefghijklmnopqrstuvwxyz"
    os.environ["BANK_REPO_PAT"] = fake_token
    os.environ["PUBLIC_REPO_PAT"] = fake_token
    os.environ["GITHUB_TOKEN"] = fake_token
    
    # Test redaction on various strings
    test_cases = [
        # (input, expected_output)
        (f"Clone URL: https://x-access-token:{fake_token}@github.com/repo", 
         "Clone URL: https://x-access-token:***REDACTED***@github.com/repo"),
        (f"Using token {fake_token} for auth",
         "Using token ***REDACTED*** for auth"),
        ("No sensitive data here", "No sensitive data here"),
        ("Token not present", "Token not present"),
    ]
    
    print("Testing redact() function:")
    print("=" * 60)
    
    errors = []
    for input_str, expected in test_cases:
        result = redact(input_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: {input_str[:60]}...")
        print(f"   Expected: {expected[:60]}...")
        print(f"   Got:      {result[:60]}...")
        if result != expected:
            errors.append(f"Mismatch: expected '{expected}', got '{result}'")
        print()
    
    print("=" * 60)
    
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("ALL TESTS PASSED!")
        return 0


def test_run_cmd_failure_redaction():
    """
    Test that run_cmd's failure path properly redacts stdout/stderr.
    We can't easily test this without mocking, but we can verify the
    redact function works on typical git error output.
    """
    print("\nTesting redaction on git-style error output:")
    print("=" * 60)
    
    fake_token = "ghp_fake1234567890abcdefghijklmnopqrstuvwxyz"
    os.environ["BANK_REPO_PAT"] = fake_token
    
    # Typical git clone failure output
    git_error = f"""fatal: could not resolve host: github.com
remote: Invalid username or password.
_token={fake_token}
https://github.com/repo/info/refs?service=git-upload-pack
Token: {fake_token}
Bearer {fake_token}"""
    
    redacted = redact(git_error)
    
    print(f"Original (with sensitive data):")
    for line in git_error.split('\n'):
        print(f"  {line}")
    print()
    print(f"Redacted:")
    for line in redacted.split('\n'):
        print(f"  {line}")
    print()
    
    # Verify token is redacted
    if fake_token in redacted:
        print(f"❌ FAILURE: Token still present in redacted output!")
        return 1
    else:
        print(f"✅ SUCCESS: Token fully redacted")
    
    # Verify token is replaced with placeholder
    if "***REDACTED***" in redacted:
        print(f"✅ SUCCESS: Redaction placeholder present")
    else:
        print(f"❌ FAILURE: Redaction placeholder missing!")
        return 1
    
    print("=" * 60)
    print("TEST PASSED!")
    return 0


if __name__ == '__main__':
    result1 = test_redact_function()
    result2 = test_run_cmd_failure_redaction()
    sys.exit(result1 or result2)
