#!/usr/bin/env python3
"""HATCHA solver — solves all 5 Monday.com reverse-CAPTCHA challenge types.

HATCHA (Hyperfast Agent Task Challenge for Access) is a reverse CAPTCHA
that verifies the caller is an AI agent, not a human. Challenges are
trivial for machines and tedious for humans.

Challenge types:
  - math:   Multiply two 5-digit numbers
  - string: Reverse a 60-80 character random string
  - count:  Count occurrences of a character in ~250 characters
  - sort:   Find the k-th smallest among 15 numbers
  - binary: Decode binary octets to ASCII text
"""

import re
from typing import Optional


def solve(text: str) -> Optional[str]:
    """Solve a HATCHA challenge from its display text.

    Args:
        text: The full challenge text as rendered on the page.

    Returns:
        The answer string, or None if the challenge type is unrecognised.
    """
    # -- sort: "Sort these numbers ascending. What is the Nth value?" --
    sort_match = re.search(r"(\d+)(?:st|nd|rd|th)\s+value", text)
    if sort_match and "sort" in text.lower():
        k = int(sort_match.group(1))
        num_line = re.search(r"(\d[\d, ]+\d)", text)
        if num_line:
            numbers = [
                int(n.strip())
                for n in num_line.group(1).split(",")
                if n.strip().isdigit()
            ]
        else:
            numbers = [int(n) for n in re.findall(r"\b\d{2,}\b", text)]
        numbers.sort()
        return str(numbers[k - 1])

    # -- math: "Multiply N × M" or "What is N × M?" --
    math_match = re.search(r"(\d+)\s*[×x*]\s*(\d+)", text)
    if math_match:
        a, b = int(math_match.group(1)), int(math_match.group(2))
        return str(a * b)

    # -- string reverse: "Reverse every character of the string below." --
    if "reverse" in text.lower():
        # Try backtick-wrapped string first, then a bare long alphanumeric line.
        m = re.search(r"`([^`]+)`", text)
        if not m:
            m = re.search(r"\n([A-Za-z0-9]{20,})\n", text)
        if m:
            return m.group(1)[::-1]

    # -- count: "Count how many times 'X' appears in ..." --
    if "count" in text.lower() or "how many" in text.lower():
        char_match = re.search(r"""[\"'](.)[\"']""", text)
        str_match = re.search(r"`([^`]+)`", text)
        if not str_match:
            str_match = re.search(r"\n([A-Za-z0-9]{20,})\n", text)
        if char_match and str_match:
            return str(str_match.group(1).count(char_match.group(1)))

    # -- binary: "Convert the binary octets to ASCII text." --
    octets = re.findall(r"[01]{8}", text)
    if octets and ("binary" in text.lower() or "ascii" in text.lower()):
        return "".join(chr(int(o, 2)) for o in octets)

    return None


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cases = [
        (
            "Sort these numbers ascending. What is the 6th value?\n"
            "1083, 319, 4801, 4637, 3052, 6050, 7253, 7224, 6488, 9250, 4526, 9495, 3277, 6275, 7380",
            "4637",
        ),
        (
            "What is 12345 × 67890?",
            str(12345 * 67890),
        ),
        (
            "Reverse every character of the string below.\n"
            "\nrDjgPF7K4SwkWGtgDuR3dXg4j3MvmEVPXYjjBPRhgMFZ2uA3n7jfguAu48Gmhv5Mq\n",
            "qM5vhmG84uAugfj7n3Au2ZFMghRPBjjYXPVEmvM3j4gXd3RuDgtGWkwS4K7FPgjDr",
        ),
        (
            "Convert the binary octets to ASCII text.\n"
            "01000001 01010011 01011001 01001110 01000011",
            "ASYNC",
        ),
    ]
    ok = 0
    for prompt, expected in cases:
        got = solve(prompt)
        status = "PASS" if got == expected else "FAIL"
        if status == "FAIL":
            print(f"  {status}: expected={expected!r}, got={got!r}")
        ok += status == "PASS"
    print(f"{ok}/{len(cases)} tests passed")

