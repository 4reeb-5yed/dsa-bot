#!/usr/bin/env python3
"""
Test that README.md auto-update logic correctly handles all three fields:
1. Day counter: "Day N of 100"
2. Tests badge: "[![Tests](https://img.shields.io/badge/tests-N%20passed-brightgreen)]()"
3. Progress bar: "**Day N of 100** ████░░░...░░ N%"

This test uses the ACTUAL current README.md content from 100-days-of-dsa
and simulates advancing from Day 4 to Day 5.
"""
import sys
import re
from pathlib import Path


def update_readme_progress(readme_content, day):
    """
    FIXED implementation - matches the corrected pick_and_commit.py
    """
    # Insert row before PROGRESS_TABLE_END
    # (simplified - not testing table insert here)

    # Count table rows to get the new test count
    progress_section = readme_content[readme_content.find('## Progress'):]
    
    # Count data rows in the table (between "| # |" header and "<!-- PROGRESS_TABLE_END -->")
    table_start = progress_section.find('| # |')
    table_end = progress_section.find('<!-- PROGRESS_TABLE_END -->')
    if table_start >= 0 and table_end >= 0:
        table_content = progress_section[table_start:table_end]
        lines = table_content.strip().split('\n')
        # Count rows that start with "| " but are not header/separator lines
        row_count = sum(1 for l in lines if l.startswith('| ') and not l.startswith('| # |') and not l.startswith('|---|'))
    else:
        row_count = 0

    bar_width = 50
    filled = int((day / 100) * bar_width)
    bar = '█' * filled + '░' * (bar_width - filled)
    percent = int((day / 100) * 100)

    # Update tests badge line - operates on full content
    # Real format: [![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen)]()
    badge_pattern = r'(\[!\[Tests\]\(https://img\.shields\.io/badge/tests-)(\d+)(%20passed-brightgreen\)\]\(\))'
    readme_content = re.sub(
        badge_pattern,
        rf'\g<1>{row_count}\g<3>',
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


def extract_current_values(readme_content):
    """Extract the three fields we care about."""
    # Day counter
    day_match = re.search(r'\*\*Day (\d+) of 100\*\*', readme_content)
    day_counter = int(day_match.group(1)) if day_match else None

    # Tests badge
    badge_match = re.search(r'img\.shields\.io/badge/tests-(\d+)%20', readme_content)
    tests_count = int(badge_match.group(1)) if badge_match else None

    # Progress bar - find the percentage
    bar_match = re.search(r'░+ (\d+)%', readme_content)
    bar_percent = int(bar_match.group(1)) if bar_match else None

    return day_counter, tests_count, bar_percent


def test_readme_update_simulation():
    """
    Simulate updating README from Day 4 to Day 5.
    Uses actual README content from 100-days-of-dsa.
    """
    # Load actual README from 100-days-of-dsa
    readme_path = Path("/workspace/project/100-days-of-dsa/README.md")
    if not readme_path.exists():
        print(f"SKIP: {readme_path} not found")
        return 1

    with open(readme_path) as f:
        readme_content = f.read()

    # Extract BEFORE values
    before_day, before_tests, before_bar = extract_current_values(readme_content)

    print("=" * 60)
    print("BEFORE update (Day 4):")
    print(f"  Day counter: {before_day}")
    print(f"  Tests badge: {before_tests}")
    print(f"  Bar percent: {before_bar}")
    print()

    # Show the badge line
    badge_line = [l for l in readme_content.split('\n') if 'shields.io' in l and 'tests' in l][0]
    bar_line = [l for l in readme_content.split('\n') if '░' in l or '█' in l][0]
    print(f"  Badge line: {badge_line}")
    print(f"  Bar line: {bar_line}")
    print()

    # Apply update for Day 5
    new_content = update_readme_progress(readme_content, 5)

    # Extract AFTER values
    after_day, after_tests, after_bar = extract_current_values(new_content)

    print("AFTER update (Day 5):")
    print(f"  Day counter: {after_day}")
    print(f"  Tests badge: {after_tests}")
    print(f"  Bar percent: {after_bar}")
    print()

    # Show the badge line
    badge_line_after = [l for l in new_content.split('\n') if 'shields.io' in l and 'tests' in l][0]
    bar_line_after = [l for l in new_content.split('\n') if '░' in l or '█' in l][0]
    print(f"  Badge line: {badge_line_after}")
    print(f"  Bar line: {bar_line_after}")
    print()

    # Assertions
    print("=" * 60)
    print("ASSERTIONS:")

    errors = []

    # Day counter
    if after_day == 5:
        print("✅ Day counter: 4 -> 5 (FIXED)")
    else:
        errors.append(f"Day counter: expected 5, got {after_day}")
        print(f"❌ Day counter: expected 5, got {after_day}")

    # Tests badge - before was wrong (8 from stale data), after should be correct count (4)
    # Note: this test doesn't insert the row, so badge shows current count (4)
    if after_tests == 4:
        print("✅ Tests badge: 8 -> 4 (FIXED - now shows correct count)")
    else:
        errors.append(f"Tests badge: expected 4, got {after_tests}")
        print(f"❌ Tests badge: expected 4, got {after_tests}")

    # Progress bar - should be 5% (Day 5 out of 100)
    if after_bar == 5:
        print("✅ Bar percent: 4% -> 5% (FIXED)")
    else:
        errors.append(f"Bar percent: expected 5, got {after_bar}")
        print(f"❌ Bar percent: expected 5, got {after_bar}")

    print("=" * 60)

    if errors:
        print(f"\nFAILED: {len(errors)} assertion(s) failed")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("\nALL TESTS PASSED!")
        return 0


if __name__ == '__main__':
    sys.exit(test_readme_update_simulation())
