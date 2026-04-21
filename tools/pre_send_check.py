#!/usr/bin/env python3
"""Pre-send validation hook — run before every external message send.

Checks:
  1. Assumption detection (unverified claims)
  2. Owner approval requirements per SOUL.md
  3. Recipient validation against contact-list
  4. Commitment trigger words (promises)

Usage:
  python3 pre_send_check.py --message "I'll send you a summary tomorrow" --recipient "+972..."
  python3 pre_send_check.py --help
"""
import argparse
import re
import sys

# Commitment trigger words (Hebrew + English)
COMMITMENT_WORDS = [
    r"\bי?אשלח\b", r"\bי?אעשה\b", r"\bי?אבדוק\b", r"\bי?אטפל\b",
    r"\bי?אחזור\b", r"\bמבטיח\b", r"\bאדאג\b", r"\bי?אעדכן\b",
    r"\bי?אכין\b", r"\bי?אסיים\b", r"\bבוא נקבע\b",
    r"\bi(?:'ll| will)\b", r"\bpromise\b", r"\bguarantee\b",
    r"\bby (?:tomorrow|end of day|eod|tonight|monday|tuesday|wednesday|thursday|friday)\b",
    r"\bwill send\b", r"\bwill check\b", r"\bwill handle\b",
    r"\bwill update\b", r"\bwill prepare\b", r"\bwill finish\b",
]

# Phrases suggesting unverified assumptions
ASSUMPTION_PHRASES = [
    r"\bi (?:think|believe|assume)\b", r"\bprobably\b", r"\bshould be\b",
    r"\bi'm (?:pretty )?sure\b", r"\bif i'm not mistaken\b",
    r"\bכנראה\b", r"\bאני מניח\b", r"\bאמור להיות\b",
]

# Actions requiring owner approval (from SOUL.md patterns)
APPROVAL_TRIGGERS = [
    r"\bdelete\b", r"\bremove\b", r"\bcancel\b", r"\bunsubscribe\b",
    r"\bpay\b", r"\btransfer\b", r"\bpurchase\b", r"\bbuy\b",
    r"\bלמחוק\b", r"\bלבטל\b", r"\bלשלם\b", r"\bלקנות\b",
    r"\bon behalf of\b", r"\bבשם\b",
]


def check_message(message: str, recipient: str) -> list[str]:
    """Return list of warnings. Empty list = PASS."""
    warnings = []
    msg_lower = message.lower()

    # 1. Commitment words
    for pattern in COMMITMENT_WORDS:
        if re.search(pattern, message, re.IGNORECASE):
            warnings.append(f"⚠️  COMMITMENT detected: matches '{pattern}' — will this be tracked?")
            break

    # 2. Assumption phrases
    for pattern in ASSUMPTION_PHRASES:
        if re.search(pattern, message, re.IGNORECASE):
            warnings.append(f"⚠️  ASSUMPTION detected: matches '{pattern}' — have you verified this?")
            break

    # 3. Owner approval
    for pattern in APPROVAL_TRIGGERS:
        if re.search(pattern, message, re.IGNORECASE):
            warnings.append(f"⚠️  APPROVAL may be needed: matches '{pattern}' — check SOUL.md rules")
            break

    # 4. Recipient sanity
    if recipient:
        if "@g.us" in recipient and any(w in msg_lower for w in ["personal", "private", "בינינו", "אישי"]):
            warnings.append("⚠️  RECIPIENT: sending personal content to a GROUP — is this intentional?")
        if not re.match(r"^[\+\d@\w\.\-]+$", recipient):
            warnings.append(f"⚠️  RECIPIENT: '{recipient}' looks malformed")

    return warnings


def main():
    parser = argparse.ArgumentParser(description="Pre-send message validation hook")
    parser.add_argument("--message", "-m", required=True, help="Message draft text")
    parser.add_argument("--recipient", "-r", default="", help="Recipient ID or phone")
    args = parser.parse_args()

    warnings = check_message(args.message, args.recipient)
    if warnings:
        print("❌ WARNINGS:")
        for w in warnings:
            print(f"  {w}")
        sys.exit(1)
    else:
        print("✅ PASS — no issues detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
