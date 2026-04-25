#!/usr/bin/env python3
"""Wiki compiler — compiles scattered knowledge into structured wiki pages.

"Compile once, query forever" — Karpathy pattern.
Instead of RAG every time, build structured wiki pages from daily notes,
project docs, and memory. Update them weekly.

Usage:
    python3 tools/wiki_compiler.py --scan            # show what needs compiling
    python3 tools/wiki_compiler.py --compile          # compile all pending topics
    python3 tools/wiki_compiler.py --compile <topic>  # compile one topic
    python3 tools/wiki_compiler.py --status           # show wiki stats
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

WORKSPACE = Path(os.environ.get('WORKSPACE', '/opt/ocana/openclaw/workspace'))
WIKI_DIR = WORKSPACE / 'wiki'
DAILY_DIR = WORKSPACE / 'memory' / 'daily'
PROJECTS_DIR = WORKSPACE / 'memory' / 'projects'
GRAPH_PATH = WORKSPACE / 'graphify-out' / 'graph.json'
INDEX_PATH = WIKI_DIR / 'index.md'


def ensure_wiki_dir():
    WIKI_DIR.mkdir(parents=True, exist_ok=True)


def scan_topics():
    """Scan daily notes and project docs for recurring topics."""
    topics = Counter()
    topic_mentions = defaultdict(list)  # topic -> [(date, line)]
    
    # Load graph communities as topic seeds
    community_topics = set()
    if GRAPH_PATH.exists():
        data = json.loads(GRAPH_PATH.read_text())
        for n in data.get('nodes', []):
            label = n.get('label', '')
            ftype = n.get('file_type', '')
            if ftype == 'document' and len(label) > 4:
                community_topics.add(label.lower())
    
    # Scan daily notes for topic mentions
    for daily in sorted(DAILY_DIR.glob('*.md')):
        date = daily.stem
        text = daily.read_text()
        for line in text.split('\n'):
            line_lower = line.lower()
            for topic in community_topics:
                if topic in line_lower:
                    topics[topic] += 1
                    topic_mentions[topic].append((date, line.strip()[:100]))
    
    # Scan project docs
    if PROJECTS_DIR.exists():
        for proj in PROJECTS_DIR.glob('*.md'):
            topic = proj.stem.replace('-', ' ')
            if topic.lower() in community_topics:
                topics[topic.lower()] += 5  # project docs weigh more
    
    return topics, topic_mentions


def get_existing_wiki_pages():
    """Get existing wiki pages and their last modified dates."""
    pages = {}
    if WIKI_DIR.exists():
        for p in WIKI_DIR.glob('*.md'):
            if p.name == 'index.md':
                continue
            pages[p.stem.lower()] = {
                'path': p,
                'modified': datetime.fromtimestamp(p.stat().st_mtime),
                'size': p.stat().st_size
            }
    return pages


def compile_topic(topic, mentions):
    """Compile a topic wiki page from all its mentions."""
    ensure_wiki_dir()
    
    # Frontmatter
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    lines = [
        '---',
        f'topic: {topic}',
        f'type: wiki',
        f'compiled: {now}',
        f'mentions: {len(mentions)}',
        '---',
        '',
        f'# {topic.title()}',
        '',
        '## Timeline',
        ''
    ]
    
    # Group by date
    by_date = defaultdict(list)
    for date, line in mentions:
        by_date[date].append(line)
    
    for date in sorted(by_date.keys(), reverse=True):
        lines.append(f'### {date}')
        for entry in by_date[date]:
            lines.append(f'- {entry}')
        lines.append('')
    
    # Related links
    lines.append('## Related')
    lines.append('')
    
    # Check graph for connections
    if GRAPH_PATH.exists():
        data = json.loads(GRAPH_PATH.read_text())
        edges = data.get('edges', data.get('links', []))
        related = set()
        for e in edges:
            src = e.get('source', '').lower()
            tgt = e.get('target', '').lower()
            if topic in src:
                related.add(tgt)
            elif topic in tgt:
                related.add(src)
        for r in sorted(related)[:10]:
            lines.append(f'- [[{r}]]')
    
    # Write
    slug = topic.replace(' ', '-').lower()
    wiki_path = WIKI_DIR / f'{slug}.md'
    wiki_path.write_text('\n'.join(lines))
    return wiki_path


def build_index():
    """Build wiki index page."""
    ensure_wiki_dir()
    pages = get_existing_wiki_pages()
    
    lines = [
        '---',
        'type: wiki-index',
        f'updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}',
        f'pages: {len(pages)}',
        '---',
        '',
        '# Wiki Index',
        '',
        f'_{len(pages)} compiled pages_',
        ''
    ]
    
    for name in sorted(pages.keys()):
        info = pages[name]
        mod = info['modified'].strftime('%Y-%m-%d')
        size = info['size']
        lines.append(f'- [[{name}]] — updated {mod}, {size} bytes')
    
    INDEX_PATH.write_text('\n'.join(lines))
    return len(pages)


def show_status():
    """Show wiki compilation status."""
    pages = get_existing_wiki_pages()
    topics, mentions = scan_topics()
    
    print(f'Wiki pages: {len(pages)}')
    print(f'Known topics: {len(topics)}')
    
    # Topics that need compiling (high mentions, no wiki page)
    needs_compile = []
    for topic, count in topics.most_common(30):
        if topic not in pages and count >= 3:
            needs_compile.append((topic, count))
    
    if needs_compile:
        print(f'\nNeed compiling ({len(needs_compile)}):')
        for topic, count in needs_compile[:15]:
            print(f'  {topic}: {count} mentions')
    
    # Stale pages (not updated in 7+ days)
    stale = []
    now = datetime.utcnow()
    for name, info in pages.items():
        age = (now - info['modified']).days
        if age > 7:
            stale.append((name, age))
    
    if stale:
        print(f'\nStale pages ({len(stale)}):')
        for name, age in sorted(stale, key=lambda x: -x[1])[:10]:
            print(f'  {name}: {age} days old')


if __name__ == '__main__':
    args = sys.argv[1:]
    
    if '--scan' in args:
        topics, mentions = scan_topics()
        print(f'Found {len(topics)} topics')
        for topic, count in topics.most_common(20):
            print(f'  {topic}: {count} mentions')
    
    elif '--compile' in args:
        topics, mentions = scan_topics()
        idx = args.index('--compile')
        if idx + 1 < len(args) and not args[idx + 1].startswith('-'):
            # Compile one topic
            topic = args[idx + 1].lower()
            if topic in mentions:
                path = compile_topic(topic, mentions[topic])
                print(f'Compiled: {path}')
            else:
                print(f'Topic "{topic}" not found')
        else:
            # Compile all topics with 3+ mentions
            compiled = 0
            pages = get_existing_wiki_pages()
            for topic, count in topics.most_common(50):
                if count >= 3 and topic not in pages:
                    path = compile_topic(topic, mentions[topic])
                    compiled += 1
                    print(f'  Compiled: {path.name} ({count} mentions)')
            build_index()
            print(f'\nCompiled {compiled} new pages')
    
    elif '--status' in args:
        show_status()
    
    else:
        print(__doc__)
