#!/usr/bin/env python3
"""
Test script for self-heal logic in pick_and_commit.py

This simulates the self-heal behavior without hitting real GitHub.
"""
import sys
from pathlib import Path
from unittest.mock import patch

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))


def test_sync_state_detects_mismatch():
    """
    Test that sync_state_from_public_repo correctly detects a mismatch
    and populates solved_ids with REAL bank IDs (not None placeholders).
    This is the critical bug fix: the old code wrote None for every
    recovered entry, silently corrupting the historical record.
    """
    # Mock bank: first 10 entries have ids matching their position for simplicity
    mock_bank = [{"id": i + 1} for i in range(15)]

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

    from pick_and_commit import sync_state_from_public_repo

    with patch('pick_and_commit.get_public_repo_solved_count', mock_get_count):
        result = sync_state_from_public_repo(state, "test/repo", "fake_token", mock_bank)

        print(f"\nBefore sync: next_index={state['next_index']}")
        print(f"Before sync: solved_ids={state['solved_ids']}")
        print(f"Sync performed: {result}")
        print(f"After sync:  next_index={state['next_index']}")
        print(f"After sync:  solved_ids={state['solved_ids']}")

        assert result == True, "Sync should have been performed"
        assert state["next_index"] == mock_public_count, (
            f"next_index should be {mock_public_count}, got {state['next_index']}"
        )

        # THE REAL ASSERTION: values must be real ids, not None
        # Before: [1, 2, 3, 4, 5]
        # After:  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        expected_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert state["solved_ids"] == expected_ids, (
            f"solved_ids should be {expected_ids}, got {state['solved_ids']}"
        )
        assert None not in state["solved_ids"], (
            f"solved_ids contains None (placeholder) — bug not fixed! Got: {state['solved_ids']}"
        )

        print("\n✅ TEST PASSED: Self-heal correctly detected mismatch and used real bank IDs")
        print(f"   solved_ids before: [1, 2, 3, 4, 5]")
        print(f"   solved_ids after:  {state['solved_ids']}")


def test_sync_state_no_mismatch():
    """Test that sync doesn't trigger when counts already match."""

    mock_bank = [{"id": i + 1} for i in range(15)]
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
        result = sync_state_from_public_repo(state, "test/repo", "fake_token", mock_bank)

        print(f"\nState before: next_index={state['next_index']}")
        print(f"Sync performed: {result}")
        print(f"State after:  next_index={state['next_index']}")

        assert result == False, "Sync should NOT have been performed when counts match"
        assert state["next_index"] == 5, "next_index should remain 5"
        assert state["solved_ids"] == [1, 2, 3, 4, 5], "solved_ids must be unchanged"

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

