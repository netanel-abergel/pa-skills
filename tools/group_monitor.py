#!/usr/bin/env python3
"""Group monitor — scans all WhatsApp groups for unanswered messages and missed actions.

Detects:
1. Messages directed at Heleni that got no response
2. Links shared by Netanel that need summarizing
3. Questions from anyone that went unanswered
4. Groups where Heleni hasn't participated in >24h despite activity

Usage:
    python3 tools/group_monitor.py                # full scan
    python3 tools/group_monitor.py --quick         # quick check (last 2h only)
    python3 tools/group_monitor.py --groups         # list all groups with status
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta
import psycopg2

DB_URL = os.environ.get('PA_DB_URL', '')
NETANEL_NAMES = {'Netanel', 'netanel'}
HELENI_NAMES = {'Heleni', 'heleni'}
URL_PATTERN = re.compile(r'https?://\S+')
QUESTION_PATTERN = re.compile(r'\?|מה |איך |למה |מתי |האם |אפשר |תוכלי|תעשי|תבדקי|תסכמי')

# Groups to skip (family etc)
SKIP_GROUPS = set()


def get_conn():
    return psycopg2.connect(DB_URL)


def get_all_groups(conn, days=7):
    """Get all active groups."""
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT chat_id FROM messages 
        WHERE chat_id LIKE '%%@g.us' 
        AND ts > NOW() - INTERVAL '%s days'
    """, (days,))
    return [r[0] for r in cur.fetchall()]


def get_recent_messages(conn, chat_id, hours=24):
    """Get recent messages for a group."""
    cur = conn.cursor()
    cur.execute("""
        SELECT sender_name, body, ts FROM messages 
        WHERE chat_id = %s AND ts > NOW() - INTERVAL '%s hours'
        ORDER BY ts ASC
    """, (chat_id, hours))
    return cur.fetchall()


def get_heleni_last(conn, chat_id):
    """Get Heleni's last message time in a group."""
    cur = conn.cursor()
    cur.execute("""
        SELECT ts FROM messages 
        WHERE chat_id = %s AND sender_name = 'Heleni'
        ORDER BY ts DESC LIMIT 1
    """, (chat_id,))
    row = cur.fetchone()
    return row[0] if row else None


def analyze_group(conn, chat_id, hours=24):
    """Analyze a group for issues."""
    messages = get_recent_messages(conn, chat_id, hours)
    heleni_last = get_heleni_last(conn, chat_id)
    
    issues = []
    
    if not messages:
        return issues
    
    saw_heleni_after = False
    
    for sender, body, ts in reversed(messages):
        if not body:
            continue
        
        is_heleni = sender in HELENI_NAMES
        if is_heleni:
            saw_heleni_after = True
            continue
        
        # Check if message needs Heleni's attention
        body_lower = body.lower()
        
        # 1. Direct mention of Heleni
        if ('הלני' in body or 'heleni' in body_lower) and not saw_heleni_after:
            issues.append({
                'type': 'mention_unanswered',
                'sender': sender,
                'body': body[:120],
                'ts': ts,
                'priority': 'high'
            })
        
        # 2. Netanel shared a link
        if sender in NETANEL_NAMES and URL_PATTERN.search(body) and not saw_heleni_after:
            issues.append({
                'type': 'netanel_link',
                'body': body[:120],
                'ts': ts,
                'priority': 'medium'
            })
        
        # 3. Question that went unanswered
        if QUESTION_PATTERN.search(body) and not saw_heleni_after:
            issues.append({
                'type': 'question_unanswered',
                'sender': sender,
                'body': body[:120],
                'ts': ts,
                'priority': 'low'
            })
    
    # 4. Group active but Heleni silent for >24h
    if heleni_last:
        gap = datetime.utcnow().replace(tzinfo=heleni_last.tzinfo) - heleni_last
        if gap.total_seconds() > 86400 and len(messages) > 3:
            issues.append({
                'type': 'silent_too_long',
                'gap_hours': int(gap.total_seconds() / 3600),
                'last_heleni': heleni_last,
                'priority': 'medium'
            })
    elif messages:
        issues.append({
            'type': 'never_participated',
            'message_count': len(messages),
            'priority': 'high'
        })
    
    return issues


def full_scan(hours=24):
    """Scan all groups and return issues."""
    conn = get_conn()
    groups = get_all_groups(conn)
    
    all_issues = {}
    for gid in groups:
        if gid in SKIP_GROUPS:
            continue
        issues = analyze_group(conn, gid, hours)
        if issues:
            all_issues[gid] = issues
    
    conn.close()
    return all_issues


def format_report(all_issues):
    """Format issues as readable report."""
    if not all_issues:
        return "All groups OK — no unanswered messages or missed actions."
    
    lines = [f"Group Monitor — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"]
    
    # Sort by priority
    high = []
    medium = []
    low = []
    
    for gid, issues in all_issues.items():
        for issue in issues:
            issue['group'] = gid
            if issue['priority'] == 'high':
                high.append(issue)
            elif issue['priority'] == 'medium':
                medium.append(issue)
            else:
                low.append(issue)
    
    if high:
        lines.append(f"HIGH ({len(high)}):")
        for i in high:
            if i['type'] == 'mention_unanswered':
                lines.append(f"  {i['group']}: {i['sender']} mentioned me — {i['body']}")
            elif i['type'] == 'never_participated':
                lines.append(f"  {i['group']}: Never participated ({i['message_count']} messages)")
        lines.append("")
    
    if medium:
        lines.append(f"MEDIUM ({len(medium)}):")
        for i in medium:
            if i['type'] == 'netanel_link':
                lines.append(f"  {i['group']}: Netanel shared link — {i['body']}")
            elif i['type'] == 'silent_too_long':
                lines.append(f"  {i['group']}: Silent {i['gap_hours']}h despite activity")
        lines.append("")
    
    if low:
        lines.append(f"LOW ({len(low)}):")
        for i in low[:5]:  # cap at 5
            if i['type'] == 'question_unanswered':
                lines.append(f"  {i['group']}: {i['sender']} asked — {i['body']}")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    args = sys.argv[1:]
    
    if '--quick' in args:
        issues = full_scan(hours=2)
    elif '--groups' in args:
        conn = get_conn()
        groups = get_all_groups(conn)
        for gid in groups:
            heleni_last = get_heleni_last(conn, gid)
            msgs = get_recent_messages(conn, gid, 24)
            status = "OK" if heleni_last and (datetime.utcnow().replace(tzinfo=heleni_last.tzinfo) - heleni_last).total_seconds() < 86400 else "NEEDS CHECK"
            print(f"{gid}: {len(msgs)} msgs/24h, heleni_last={heleni_last}, status={status}")
        conn.close()
        sys.exit(0)
    else:
        issues = full_scan(hours=24)
    
    report = format_report(issues)
    print(report)
