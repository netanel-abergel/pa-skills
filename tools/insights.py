#!/usr/bin/env python3
"""
insights.py — Structured self-report: patterns, failures, recall gaps, and trends.

Usage:
  python3 tools/insights.py [--days N]
"""
import os, sys, argparse, sqlite3, json, datetime, glob

DAILY_DIR = "/opt/ocana/openclaw/workspace/memory/daily"
LEARNINGS_DIR = "/opt/ocana/openclaw/workspace/.learnings"
SQLITE_DB = "/opt/ocana/openclaw/memory/main.sqlite"

def count_daily_entries(days=7):
    """Count entries in daily notes over the last N days."""
    today = datetime.date.today()
    entries = 0
    files_found = 0
    for i in range(days):
        d = today - datetime.timedelta(days=i)
        path = os.path.join(DAILY_DIR, f"{d.isoformat()}.md")
        if os.path.exists(path):
            files_found += 1
            with open(path) as f:
                for line in f:
                    if line.strip().startswith('[') and 'IL]' in line:
                        entries += 1
    return {'days_covered': files_found, 'total_entries': entries, 'avg_per_day': round(entries / max(files_found, 1), 1)}

def analyze_learnings():
    """Analyze .learnings/ files for patterns."""
    results = {'corrections': 0, 'failures': 0, 'patterns': 0, 'recent': []}
    for fname in ['LEARNINGS.md', 'ERRORS.md']:
        fpath = os.path.join(LEARNINGS_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            content = f.read()
        for line in content.split('\n'):
            if '| correction |' in line:
                results['corrections'] += 1
            elif '| failure |' in line or '| skill_failure |' in line:
                results['failures'] += 1
            elif '| pattern |' in line:
                results['patterns'] += 1
    return results

def memory_coverage():
    """Check how well memory sources cover recent history."""
    today = datetime.date.today()
    coverage = {'daily_notes': 0, 'missing_days': []}
    for i in range(14):
        d = today - datetime.timedelta(days=i)
        path = os.path.join(DAILY_DIR, f"{d.isoformat()}.md")
        if os.path.exists(path):
            coverage['daily_notes'] += 1
        else:
            coverage['missing_days'].append(d.isoformat())
    
    # Check SQLite index freshness
    try:
        db = sqlite3.connect(SQLITE_DB)
        cur = db.cursor()
        cur.execute("SELECT count(*) FROM chunks")
        coverage['indexed_chunks'] = cur.fetchone()[0]
        cur.execute("SELECT count(DISTINCT path) FROM chunks")
        coverage['indexed_files'] = cur.fetchone()[0]
        cur.execute("SELECT max(updated_at) FROM chunks")
        coverage['last_index_update'] = cur.fetchone()[0]
        db.close()
    except Exception as e:
        coverage['index_error'] = str(e)
    
    return coverage

def whatsapp_stats(days=7):
    """Get WhatsApp message volume stats."""
    pa_db_url = os.environ.get('PA_DB_URL')
    if not pa_db_url:
        return {'error': 'PA_DB_URL not set'}
    try:
        import psycopg2
        conn = psycopg2.connect(pa_db_url)
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                count(*) as total,
                count(*) FILTER (WHERE is_from_me) as sent,
                count(*) FILTER (WHERE NOT is_from_me) as received,
                count(DISTINCT chat_id) as unique_chats
            FROM messages 
            WHERE ts > NOW() - INTERVAL '%s days'
        """, (days,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return {
            'total': row[0], 'sent': row[1], 'received': row[2],
            'unique_chats': row[3], 'period_days': days
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    report = {
        'period': f'Last {args.days} days',
        'generated': datetime.datetime.now().isoformat(),
        'daily_activity': count_daily_entries(args.days),
        'learnings': analyze_learnings(),
        'memory_coverage': memory_coverage(),
        'whatsapp': whatsapp_stats(args.days)
    }

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"=== Insights Report ({report['period']}) ===\n")
        
        da = report['daily_activity']
        print(f"Daily Activity: {da['total_entries']} entries across {da['days_covered']} days (avg {da['avg_per_day']}/day)")
        
        le = report['learnings']
        print(f"Learnings: {le['corrections']} corrections, {le['failures']} failures, {le['patterns']} patterns")
        
        mc = report['memory_coverage']
        print(f"Memory: {mc['daily_notes']}/14 daily notes present, {mc.get('indexed_chunks', '?')} chunks indexed across {mc.get('indexed_files', '?')} files")
        if mc['missing_days']:
            print(f"  Missing days: {', '.join(mc['missing_days'][:5])}")
        
        wa = report['whatsapp']
        if 'error' not in wa:
            print(f"WhatsApp: {wa['total']} messages ({wa['sent']} sent, {wa['received']} received) across {wa['unique_chats']} chats")
        
        print()

if __name__ == '__main__':
    main()
