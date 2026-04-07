#!/usr/bin/env python3
"""
Dedup check for queued message double-delivery bug (OpenClaw issue #34041).
Usage: python3 dedup_check.py <message_id>
Exit 0 = already seen (should NO_REPLY)
Exit 1 = new message (proceed normally)

File stays small: TTL-based cleanup on every read + hard cap of 200 entries.
"""
import sys, json, os, time

DEDUP_FILE = "/tmp/heleni_dedup.json"
TTL_SECONDS = 120
MAX_ENTRIES = 200

def load():
    try:
        data = json.load(open(DEDUP_FILE))
        now = time.time()
        # Remove expired entries
        cleaned = {k: v for k, v in data.items() if now - v < TTL_SECONDS}
        # Hard cap: keep only the MAX_ENTRIES most recent
        if len(cleaned) > MAX_ENTRIES:
            sorted_entries = sorted(cleaned.items(), key=lambda x: x[1], reverse=True)
            cleaned = dict(sorted_entries[:MAX_ENTRIES])
        return cleaned
    except:
        return {}

def save(data):
    with open(DEDUP_FILE, "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    msg_id = sys.argv[1] if len(sys.argv) > 1 else ""
    if not msg_id:
        sys.exit(1)
    data = load()
    if msg_id in data:
        sys.exit(0)  # already seen → NO_REPLY
    data[msg_id] = time.time()
    save(data)
    sys.exit(1)  # new → proceed
