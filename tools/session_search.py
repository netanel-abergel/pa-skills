#!/usr/bin/env python3
"""
session_search.py — Full-text + semantic search across all memory sources.
Searches: SQLite FTS5 (memory files), PostgreSQL (WhatsApp history), daily notes.

Usage:
  python3 tools/session_search.py "search query" [--limit N] [--days N]
"""
import os, sys, argparse, sqlite3, json

SQLITE_DB = "/opt/ocana/openclaw/memory/main.sqlite"
DAILY_DIR = "/opt/ocana/openclaw/workspace/memory/daily"

def search_fts(query, limit=10):
    """Search SQLite FTS5 index across all memory files."""
    results = []
    try:
        db = sqlite3.connect(SQLITE_DB)
        cur = db.cursor()
        # FTS5 match search
        cur.execute("""
            SELECT c.path, c.start_line, c.end_line, c.text,
                   rank
            FROM chunks_fts 
            JOIN chunks c ON chunks_fts.rowid = c.rowid
            WHERE chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        for path, start, end, text, rank in cur.fetchall():
            results.append({
                'source': 'memory',
                'path': path,
                'lines': f"{start}-{end}",
                'text': text[:500],
                'score': round(-rank, 3)
            })
        db.close()
    except Exception as e:
        print(f"FTS search error: {e}", file=sys.stderr)
    return results

def search_postgres(query, limit=10, days=30):
    """Search PostgreSQL WhatsApp message history."""
    results = []
    pa_db_url = os.environ.get('PA_DB_URL')
    if not pa_db_url:
        return results
    try:
        import psycopg2
        conn = psycopg2.connect(pa_db_url)
        cur = conn.cursor()
        # Use ILIKE for flexible text search
        search_terms = query.split()
        where_clauses = []
        params = []
        for term in search_terms[:5]:  # max 5 terms
            where_clauses.append("body ILIKE %s")
            params.append(f"%{term}%")
        
        where = " AND ".join(where_clauses)
        params.append(days)
        params.append(limit)
        
        cur.execute(f"""
            SELECT body, ts, chat_id, is_from_me 
            FROM messages 
            WHERE {where}
              AND ts > NOW() - INTERVAL '%s days'
            ORDER BY ts DESC 
            LIMIT %s
        """, params)
        
        for body, ts, chat_id, is_from_me in cur.fetchall():
            results.append({
                'source': 'whatsapp',
                'chat_id': chat_id,
                'from_me': is_from_me,
                'ts': str(ts),
                'text': body[:500]
            })
        cur.close()
        conn.close()
    except Exception as e:
        print(f"PostgreSQL search error: {e}", file=sys.stderr)
    return results

def search_daily_notes(query, limit=10):
    """Grep search through daily notes."""
    results = []
    if not os.path.isdir(DAILY_DIR):
        return results
    
    terms = query.lower().split()
    for fname in sorted(os.listdir(DAILY_DIR), reverse=True):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(DAILY_DIR, fname)
        try:
            with open(fpath) as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if all(t in line.lower() for t in terms[:3]):
                    results.append({
                        'source': 'daily',
                        'file': fname,
                        'line': i + 1,
                        'text': line.strip()[:500]
                    })
                    if len(results) >= limit:
                        return results
        except Exception:
            continue
    return results

def main():
    parser = argparse.ArgumentParser(description='Search across all memory sources')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--limit', type=int, default=10, help='Max results per source')
    parser.add_argument('--days', type=int, default=30, help='Days to search in WhatsApp')
    parser.add_argument('--source', choices=['all', 'memory', 'whatsapp', 'daily'], default='all')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    all_results = {}
    
    if args.source in ('all', 'memory'):
        all_results['memory'] = search_fts(args.query, args.limit)
    
    if args.source in ('all', 'whatsapp'):
        all_results['whatsapp'] = search_postgres(args.query, args.limit, args.days)
    
    if args.source in ('all', 'daily'):
        all_results['daily'] = search_daily_notes(args.query, args.limit)

    if args.json:
        print(json.dumps(all_results, indent=2, default=str))
    else:
        total = sum(len(v) for v in all_results.values())
        print(f"Found {total} results for: {args.query}\n")
        
        for source, results in all_results.items():
            if results:
                print(f"=== {source.upper()} ({len(results)} results) ===")
                for r in results:
                    if source == 'memory':
                        print(f"  [{r['path']}:{r['lines']}] (score:{r['score']})")
                        print(f"    {r['text'][:200]}")
                    elif source == 'whatsapp':
                        sender = "ME" if r['from_me'] else r['chat_id']
                        print(f"  [{r['ts']}] [{sender}]")
                        print(f"    {r['text'][:200]}")
                    elif source == 'daily':
                        print(f"  [{r['file']}:{r['line']}]")
                        print(f"    {r['text'][:200]}")
                    print()

if __name__ == '__main__':
    main()
