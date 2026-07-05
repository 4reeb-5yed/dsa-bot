#!/usr/bin/env python3
"""
Test script for self-heal logic in pick_and_commit.py

This simulates the self-heal behavior without hitting real GitHub.
"""
import sys
import subprocess
import json
from pathlib import Path
from unittest.mock import patch

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the functions we need to test
# We'll mock the actual git/github calls

def test_sync_state_detects_mismatch():
    """Test that sync_state_from_public_repo correctly detects and heals a mismatch."""
    
    # Simulate: public repo has 10 solved days, but state.json has next_index=5
    mock_public_count = 10
    
    state = {
        "next_index": 5,
        "solved_ids": [1, 2, 3, 4, 5],
        "last_run_date": None
    }
    
    def mock_get_count(repo, token):
        print(f"[MOCK] get_public_repo_solved_count called, returning {mock_public_count}")
        return mock_public_count
    
    # Manually test the sync logic
    from pick_and_commit import sync_state_from_public_repo
    
    # Patch the function
    with patch('pick_and_commit.get_public_repo_solved_count', mock_get_count):
        result = sync_state_from_public_repo(state, "test/repo", "fake_token")
        
        print(f"\nBefore sync: next_index={state['next_index']}, solved_ids count={len(state['solved_ids'])}")
        print(f"Sync performed: {result}")
        print(f"After sync: next_index={state['next_index']}, solved_ids count={len(state['solved_ids'])}")
        
        assert result == True, "Sync should have been performed"
        assert state["next_index"] == mock_public_count, f"next_index should be {mock_public_count}, got {state['next_index']}"
        assert len(state["solved_ids"]) == mock_public_count, f"solved_ids should have {mock_public_count} entries"
        
        print("\n✅ TEST PASSED: Self-heal correctly detected mismatch and recovered")


def test_sync_state_no_mismatch():
    """Test that sync doesn't trigger when counts match."""
    
    mock_public_count = 5
    
    state = {
        "next_index": 5,
        "solved_ids": [1, 2, 3, 4, 5],
        "last_run_date": None
    }
    
    def mock_get_count(repo, token):
        print(f"[MOCK] get_public_repo_solved_count called, returning {mock_public_count}")
        return mock_public_count
    
    from pick_and_commit import sync_state_from_public_repo
    
    with patch('pick_and_commit.get_public_repo_solved_count', mock_get_count):
        result = sync_state_from_public_repo(state, "test/repo", "fake_token")
        
        print(f"\nState before: next_index={state['next_index']}")
        print(f"Sync performed: {result}")
        print(f"State after: next_index={state['next_index']}")
        
        assert result == False, "Sync should NOT have been performed when counts match"
        assert state["next_index"] == 5, "next_index should remain 5"
        
        print("\n✅ TEST PASSED: No sync when counts already match")


if __name__ == '__main__':
    print("=" * 60)
    print("Testing self-heal logic")
    print("=" * 60)
    
    test_sync_state_detects_mismatch()
    print()
    test_sync_state_no_mismatch()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
