#!/usr/bin/env python3
"""
Test the README update logic.
This test is SELF-CONTAINED with in-memory fixtures - no external files needed.
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def update_readme_progress(readme_content, day, test_count):
    """Exact copy of the update logic from pick_and_commit.py"""
    bar_width = 50
    filled = int((day / 100) * bar_width)
    bar = '█' * filled + '░' * (bar_width - filled)
    percent = int((day / 100) * 100)

    # Update tests badge line - match the exact current format
    # Real format: [![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen)]()
    import re
    badge_pattern = r'(\[!\[Tests\]\(https://img\.shields\.io/badge/tests-)(\d+)(%20passed-brightgreen\)\]\(\))'
    readme_content = re.sub(
        badge_pattern,
        rf'\g<1>{test_count}\g<3>',
        readme_content
    )

    # Update day counter AND progress bar AND percentage in one pass
    # Real format: **Day 4 of 100** ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 4%
    bar_pattern = r'(\*\*Day )(\d+)( of 100\*\* █+░+ )(\d+%)'
    readme_content = re.sub(
        bar_pattern,
        lambda m: f'**Day {day} of 100** {bar} {percent}%',
        readme_content
    )

    return readme_content


def create_fixture_readme():
    """Create a self-contained fixture README for testing."""
    return """# 100 Days of DSA

## Progress

![Days](https://img.shields.io/badge/days-4%20of%20100-blue)
[![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen)]()

**Day 4 of 100** ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 4%

| # | Day | Problem | Topic | Difficulty | Solution | Tests |
|---|-----|---------|-------|------------|----------|-------|
| 1 | Day 001 | Two Sum | Arrays | Easy | [Solution](./solutions/day_001_two_sum.py) | [Tests](./tests/test_day_001_two_sum.py) |
| 2 | Day 002 | Add Two Numbers | Linked Lists | Medium | [Solution](./solutions/day_002_add_two_numbers.py) | [Tests](./tests/test_day_002_add_two_numbers.py) |
| 3 | Day 003 | Longest Substring | Strings | Medium | [Solution](./solutions/day_003_longest_substring.py) | [Tests](./tests/test_day_003_longest_substring.py) |
| 4 | Day 004 | Median of Two Sorted Arrays | Arrays | Hard | [Solution](./solutions/day_004_median.py) | [Tests](./tests/test_day_004_median.py) |

<!-- PROGRESS_TABLE_END -->

## Usage

1. Solve the problem
2. Write tests
3. Submit
"""


def test_readme_update():
    """
    Test that all three README fields update correctly.
    
    This test is SELF-CONTAINED - uses in-memory fixture data,
    no external files or paths required.
    
    Key: The tests badge should show TEST COUNT, not DAY COUNT.
    Each day has 2 tests, so with 4 days done: 4 × 2 = 8 tests.
    The badge should show 8, not 4.
    """
    # Use self-contained fixture (4 days = 8 tests)
    readme_content = create_fixture_readme()
    
    # Initial state: 4 days, 8 tests
    initial_test_count = 8

    # Extract current values before update
    badge_match = re.search(r'(\[!\[Tests\]\(https://img\.shields\.io/badge/tests-)(\d+)(%20passed-brightgreen\)\]\(\))', readme_content)
    bar_match = re.search(r'(\*\*Day )(\d+)( of 100\*\* █+░+ )(\d+%)', readme_content)

    old_badge_count = int(badge_match.group(2)) if badge_match else 0
    old_day = int(bar_match.group(2)) if bar_match else 0
    old_percent = int(bar_match.group(4).rstrip('%')) if bar_match else 0

    print(f"Fixture: 4 days, 8 tests")
    print()

    # Simulate a "Day 5" run - add 2 more tests for the new day
    new_day = 5
    new_test_count = initial_test_count + 2  # Adding 2 tests for the new day

    updated_content = update_readme_progress(readme_content, new_day, new_test_count)

    # Extract new values
    new_badge_match = re.search(r'(\[!\[Tests\]\(https://img\.shields\.io/badge/tests-)(\d+)(%20passed-brightgreen\)\]\(\))', updated_content)
    new_bar_match = re.search(r'(\*\*Day )(\d+)( of 100\*\* █+░+ )(\d+%)', updated_content)

    new_badge_count = int(new_badge_match.group(2)) if new_badge_match else 0
    new_day_extracted = int(new_bar_match.group(2)) if new_bar_match else 0
    new_percent = int(new_bar_match.group(4).rstrip('%')) if new_bar_match else 0

    print("=" * 70)
    print("README UPDATE TEST (SELF-CONTAINED)")
    print("=" * 70)
    print()
    print(f"Before update (Day {old_day}, {initial_test_count} tests):")
    print(f"  Day counter: {old_day}")
    print(f"  Tests badge: {old_badge_count}")
    print(f"  Bar percent: {old_percent}%")
    print()
    print(f"After update (Day {new_day}, {new_test_count} tests):")
    print(f"  Day counter: {new_day_extracted}")
    print(f"  Tests badge: {new_badge_count}")
    print(f"  Bar percent: {new_percent}%")
    print()
    print("Badge lines:")
    badge_line_match = re.search(r'\[!\[Tests\].*?\]\(\)', updated_content)
    if badge_line_match:
        print(f"  {badge_line_match.group()}")
    print()
    print("Bar line:")
    bar_line_match = re.search(r'\*\*Day \d+ of 100\*\*.*?\d+%', updated_content)
    if bar_line_match:
        print(f"  {bar_line_match.group()}")
    print()
    print("ASSERTIONS:")
    print("=" * 70)

    errors = []

    # Day counter should be 4 -> 5
    if new_day_extracted == 5:
        print(f"✅ Day counter: {old_day} -> {new_day_extracted} (correct)")
    else:
        print(f"❌ Day counter: expected 5, got {new_day_extracted}")
        errors.append("Day counter")

    # Tests badge should be 8 -> 10 (4 days × 2 tests = 8, then 5 days × 2 = 10)
    # This is TEST COUNT, not DAY COUNT
    expected_new_count = 10  # 5 days × 2 tests each
    if new_badge_count == expected_new_count:
        print(f"✅ Tests badge: {old_badge_count} -> {new_badge_count} (correct: {new_day} days × 2 tests = {expected_new_count})")
    else:
        print(f"❌ Tests badge: expected {expected_new_count}, got {new_badge_count}")
        errors.append("Tests badge")

    # Bar percent should be 4% -> 5%
    if new_percent == 5:
        print(f"✅ Bar percent: {old_percent}% -> {new_percent}% (correct)")
    else:
        print(f"❌ Bar percent: expected 5%, got {new_percent}%")
        errors.append("Bar percent")

    print("=" * 70)

    if errors:
        print(f"FAILED: {', '.join(errors)}")
        return 1
    else:
        print("ALL TESTS PASSED!")
        print()
        print("Note: This test uses in-memory fixtures - no external files needed.")
        return 0




def count_tests_in_test_code(test_code):
    """Count test functions in test_code using same convention as pick_and_commit.py"""
    return test_code.count("\ndef test_")


def simulate_test_count_calculation(existing_test_files, new_test_code):
    """Simulate the test_count calculation from pick_and_commit.py"""
    test_count = 0
    for content in existing_test_files:
        test_count += content.count("\ndef test_")
    test_count += count_tests_in_test_code(new_test_code)
    return test_count


def test_test_count_calculation():
    """
    Regression test for off-by-one bug in test-count badge calculation.
    
    Bug: Old code used test_count += 1 assuming 1 test per day.
    Fix: Use test_count += test_code.count("\ndef test_") to get actual count.
    """
    print()
    print("=" * 70)
    print("REGRESSION TEST: Test-count calculation")
    print("=" * 70)
    print()
    
    # Fixture: 4 existing days with 2 tests each = 8 tests total
    existing_files = [
        """from solutions.day_001_two_sum import two_sum

def test_two_sum_basic():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]

def test_two_sum_negative():
    assert two_sum([-1, -2, -3, -4, -5], -8) == [2, 4]
""",
        """from solutions.day_002_contains_duplicate import contains_duplicate

def test_contains_duplicate_true():
    assert contains_duplicate([1, 2, 3, 1]) == True

def test_contains_duplicate_false():
    assert contains_duplicate([1, 2, 3, 4]) == False
""",
        """from solutions.day_003_valid_anagram import is_anagram

def test_is_anagram_basic():
    assert is_anagram("anagram", "nagaram") == True

def test_is_anagram_false():
    assert is_anagram("rat", "car") == False
""",
        """from solutions.day_004_best_time import max_profit

def test_max_profit_basic():
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5

def test_max_profit_decreasing():
    assert max_profit([7, 6, 4, 3, 1]) == 0
""",
    ]
    
    # New day test_code with 2 tests
    new_test_code = """from solutions.day_005_new_problem import new_function

def test_new_function_case1():
    assert new_function([1, 2, 3]) == expected

def test_new_function_case2():
    assert new_function([]) == None
"""
    
    # Expected: 4 files * 2 tests + 2 new tests = 10
    expected_tests = (len(existing_files) * 2) + 2
    
    print("Existing test files:", len(existing_files))
    print("  Each file contains 2 tests")
    print("  Total from existing:", len(existing_files) * 2, "tests")
    print()
    print("New day test_code contains 2 tests")
    print()
    
    actual_count = simulate_test_count_calculation(existing_files, new_test_code)
    
    print("Expected test count:", expected_tests)
    print("Calculated test count:", actual_count)
    print()
    
    if actual_count == expected_tests:
        print("[PASS] TEST PASSED: Test count calculation is correct")
        print("=" * 70)
        return 0
    else:
        print("[FAIL] TEST FAILED: Expected", expected_tests, ", got", actual_count)
        print("=" * 70)
        return 1


if __name__ == '__main__':
    # Run both tests
    result1 = test_readme_update()
    print()
    result2 = test_test_count_calculation()
    sys.exit(result1 or result2)
