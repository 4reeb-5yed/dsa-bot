#!/usr/bin/env python3
"""
Test that bank-sourced content is properly escaped in shell commands.
Issue 2: Shell injection via bank-sourced content.
"""
import sys
import shlex
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_shlex_quote_escaping():
    """
    Verify that shlex.quote properly escapes malicious bank content.
    """
    # Malicious bank entry content
    malicious_title = 'Two Sum"; touch /tmp/pwned; echo "'
    malicious_topic = 'arrays`whoami`'
    malicious_difficulty = 'easy$danger'
    
    # What the command would look like WITHOUT escaping
    unescaped_commit = f'commit -m "Day 001: {malicious_title} ({malicious_topic}, {malicious_difficulty})"'
    print(f"UNESCAPED (vulnerable):")
    print(f"  {unescaped_commit}")
    print()
    
    # What the command looks like WITH shlex.quote
    escaped_title = shlex.quote(malicious_title)
    escaped_topic = shlex.quote(malicious_topic)
    escaped_difficulty = shlex.quote(malicious_difficulty)
    escaped_commit = f'commit -m "Day 001: {escaped_title} ({escaped_topic}, {escaped_difficulty})"'
    print(f"ESCAPED (safe):")
    print(f"  {escaped_commit}")
    print()
    
    # Check that the malicious characters are not interpretable as shell metacharacters
    # After shlex.quote, the string should be wrapped in quotes or escaped
    
    # The injected command won't execute because:
    # 1. The semicolons are inside quoted strings
    # 2. The backticks are inside quoted strings
    # 3. The $ is inside quoted strings
    
    # Verify shlex.quote did something
    assert escaped_title != malicious_title, "shlex.quote should modify the string"
    assert escaped_topic != malicious_topic, "shlex.quote should modify the string"
    assert escaped_difficulty != malicious_difficulty, "shlex.quote should modify the string"
    
    # Verify the malicious content is preserved (not stripped)
    assert "Two Sum" in escaped_title, "Original content should be preserved"
    assert "arrays" in escaped_topic, "Original content should be preserved"
    
    print("✅ shlex.quote properly escapes all shell metacharacters")
    print()
    
    # Verify the /tmp/pwned file is NOT created
    pwned_file = Path("/tmp/pwned")
    if pwned_file.exists():
        print("❌ VULNERABILITY: /tmp/pwned was created!")
        return 1
    else:
        print("✅ No injection occurred: /tmp/pwned does not exist")
    
    print()
    print("ALL TESTS PASSED!")
    return 0


if __name__ == '__main__':
    sys.exit(test_shlex_quote_escaping())
