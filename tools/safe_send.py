#!/usr/bin/env python3
"""Safe send — filters thinking from outbound messages.

Usage:
  python3 tools/safe_send.py "message text here"
  
Returns cleaned message to stdout. Exit 0 = clean, exit 1 = had thinking removed.
If the entire message is thinking, outputs empty string.
"""
import re
import sys

# Patterns that indicate internal reasoning / thinking
THINKING_PATTERNS = [
    # English thinking verbs
    r"(?:^|\. )I (?:need to|should|will|already|notice|can see|flagged|told|escalated|identified|checked|see that|think|believe)",
    r"(?:^|\. )(?:Let me|Looking at|First I|Here's my|Based on|The (?:problem|issue|bug) is)",
    r"(?:^|\. )(?:They'?re not listening|stuck in a.*loop|not responding to)",
    # Describing internal actions to third parties
    r"(?:^|\. )I (?:sent|reported|updated|asked|messaged|contacted|pinged|DMed) (?:him|her|them|Netanel|the owner)",
    r"(?:^|\. )(?:Already flagged|Already told|Already sent|Already reported)",
    # Hebrew thinking
    r"(?:^|[.!?] )(?:בודקת|זיהיתי|הבעיה היא|צריכה ל|אני רואה ש|שלחתי ל|דיווחתי ל|עדכנתי את|בדקתי ו)",
    r"(?:^|[.!?] )(?:אני צריכה|אני חושבת|נראה לי ש|הסיבה היא)",
]

COMPILED = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in THINKING_PATTERNS]


def clean_message(msg: str) -> tuple[str, bool]:
    """Remove sentences containing thinking. Returns (cleaned, had_thinking)."""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?\n])\s*', msg)
    clean = []
    removed = False
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        is_thinking = False
        for pattern in COMPILED:
            if pattern.search(sentence):
                is_thinking = True
                removed = True
                break
        if not is_thinking:
            clean.append(sentence)
    
    return '\n'.join(clean) if clean else '', removed


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 safe_send.py 'message'", file=sys.stderr)
        sys.exit(2)
    
    msg = sys.argv[1]
    cleaned, had_thinking = clean_message(msg)
    
    if cleaned:
        print(cleaned)
    
    sys.exit(1 if had_thinking else 0)


if __name__ == "__main__":
    main()
