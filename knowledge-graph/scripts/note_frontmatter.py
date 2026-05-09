#!/usr/bin/env python3
"""Frontmatter adder — adds structured metadata to notes.

Adds YAML frontmatter with type, tags, and timestamps to daily notes,
project docs, and other markdown files. Enables structured queries
like "all notes about X" without scanning content.

Usage:
    python3 tools/note_frontmatter.py --daily          # add frontmatter to today's daily
    python3 tools/note_frontmatter.py --all-daily       # add frontmatter to all daily notes
    python3 tools/note_frontmatter.py --projects        # add frontmatter to project docs
    python3 tools/note_frontmatter.py --query type=daily tag=graphify  # query by frontmatter
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

WORKSPACE = Path(os.environ.get('WORKSPACE', '/path/to/openclaw/workspace'))
DAILY_DIR = WORKSPACE / 'memory' / 'daily'
PROJECTS_DIR = WORKSPACE / 'memory' / 'projects'

# Auto-tagging rules: keyword -> tag
TAG_RULES = {
    'graphify': 'graphify',
    'knowledge graph': 'graphify',
    'cron': 'crons',
    'heartbeat': 'ops',
    'gateway': 'ops',
    'whatsapp': 'whatsapp',
    'calendar': 'calendar',
    'linkedin': 'content',
    'substack': 'content',
    'monday.com': 'monday',
    'onboarding': 'onboarding',
    'PA ': 'pa-network',
    'vertex': 'infra',
    'litellm': 'infra',
    'memory': 'memory',
    'eval': 'eval',
    'auto_improve': 'self-improve',
    'skill': 'skills',
    'owner': 'owner',
}


def has_frontmatter(text):
    """Check if text already has YAML frontmatter."""
    return text.strip().startswith('---')


def extract_tags(text):
    """Auto-extract tags from content."""
    tags = set()
    text_lower = text.lower()
    for keyword, tag in TAG_RULES.items():
        if keyword.lower() in text_lower:
            tags.add(tag)
    return sorted(tags)


def add_frontmatter(filepath, note_type='note', extra_tags=None):
    """Add or update frontmatter on a file."""
    p = Path(filepath)
    if not p.exists():
        return False
    
    text = p.read_text()
    
    # Skip if already has frontmatter
    if has_frontmatter(text):
        return False
    
    tags = extract_tags(text)
    if extra_tags:
        tags = sorted(set(tags) | set(extra_tags))
    
    # Build frontmatter
    mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d')
    
    fm_lines = ['---']
    fm_lines.append(f'type: {note_type}')
    
    if note_type == 'daily':
        # Extract date from filename
        date = p.stem
        fm_lines.append(f'date: {date}')
        # Count entries
        entries = len([l for l in text.split('\n') if l.strip().startswith('[')])
        fm_lines.append(f'entries: {entries}')
    
    if tags:
        fm_lines.append(f'tags: [{", ".join(tags)}]')
    
    fm_lines.append(f'modified: {mtime}')
    fm_lines.append('---')
    fm_lines.append('')
    
    new_text = '\n'.join(fm_lines) + text
    p.write_text(new_text)
    return True


def query_frontmatter(**kwargs):
    """Query files by frontmatter fields."""
    results = []
    
    # Search all md files in memory/
    search_dirs = [DAILY_DIR, PROJECTS_DIR]
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for f in search_dir.glob('*.md'):
            text = f.read_text()
            if not has_frontmatter(text):
                continue
            
            # Parse frontmatter
            fm_match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if not fm_match:
                continue
            
            fm_text = fm_match.group(1)
            match = True
            for key, value in kwargs.items():
                pattern = f'{key}:.*{re.escape(value)}'
                if not re.search(pattern, fm_text, re.IGNORECASE):
                    match = False
                    break
            
            if match:
                results.append(f)
    
    return results


if __name__ == '__main__':
    args = sys.argv[1:]
    
    if '--daily' in args:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        daily = DAILY_DIR / f'{today}.md'
        if daily.exists():
            if add_frontmatter(daily, 'daily'):
                print(f'Added frontmatter to {daily.name}')
            else:
                print(f'{daily.name} already has frontmatter')
        else:
            print(f'No daily note for {today}')
    
    elif '--all-daily' in args:
        added = 0
        for f in sorted(DAILY_DIR.glob('*.md')):
            if add_frontmatter(f, 'daily'):
                added += 1
                tags = extract_tags(f.read_text())
                print(f'  {f.name}: tags={tags}')
        print(f'\nAdded frontmatter to {added} daily notes')
    
    elif '--projects' in args:
        if PROJECTS_DIR.exists():
            added = 0
            for f in sorted(PROJECTS_DIR.glob('*.md')):
                if add_frontmatter(f, 'project'):
                    added += 1
                    print(f'  {f.name}')
            print(f'\nAdded frontmatter to {added} project docs')
    
    elif '--query' in args:
        idx = args.index('--query')
        query_args = {}
        for a in args[idx + 1:]:
            if '=' in a:
                k, v = a.split('=', 1)
                query_args[k] = v
        results = query_frontmatter(**query_args)
        print(f'Found {len(results)} files:')
        for r in results:
            print(f'  {r.relative_to(WORKSPACE)}')
    
    else:
        print(__doc__)
