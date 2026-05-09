#!/usr/bin/env python3
"""Auto cross-linker — adds [[wikilinks]] to notes for known concepts.

Scans a file and replaces bare mentions of known concepts with [[wikilinks]].
Concepts come from: graphify nodes, skill names, contact names, project names.

Usage:
    python3 tools/wiki_crosslinker.py <file>           # crosslink one file
    python3 tools/wiki_crosslinker.py --daily           # crosslink today's daily note
    python3 tools/wiki_crosslinker.py --all-daily       # crosslink all daily notes
    python3 tools/wiki_crosslinker.py --build-index     # rebuild concept index
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.environ.get('WORKSPACE', '/path/to/openclaw/workspace'))
INDEX_PATH = WORKSPACE / 'graphify-out' / 'concept-index.json'
GRAPH_PATH = WORKSPACE / 'graphify-out' / 'graph.json'
SKILLS_DIR = WORKSPACE / 'skills'
DAILY_DIR = WORKSPACE / 'memory' / 'daily'
WIKI_DIR = WORKSPACE / 'wiki'

# Concepts to never wikilink (too generic)
STOP_WORDS = {
    'get', 'set', 'run', 'load', 'save', 'main', 'test', 'error', 'data',
    'file', 'path', 'name', 'type', 'list', 'node', 'edge', 'api', 'url',
    'key', 'value', 'true', 'false', 'null', 'none', 'self', 'class',
    'the', 'and', 'for', 'with', 'from', 'this', 'that', 'not', 'but',
    'action', 'question', 'conversation', 'status', 'index', 'result'
}

def build_index():
    """Build concept index from graph nodes, skills, contacts, projects."""
    concepts = {}
    
    # From graphify nodes (only document/paper type, skip code internals)
    if GRAPH_PATH.exists():
        data = json.loads(GRAPH_PATH.read_text())
        for n in data.get('nodes', []):
            label = n.get('label', '')
            ftype = n.get('file_type', '')
            if ftype in ('document', 'paper') and len(label) > 3:
                key = label.lower().strip()
                if key not in STOP_WORDS:
                    concepts[key] = label
    
    # From skill names
    if SKILLS_DIR.exists():
        for p in SKILLS_DIR.iterdir():
            if p.is_dir() and (p / 'SKILL.md').exists():
                concepts[p.name.lower()] = p.name
    
    # From project memory files
    proj_dir = WORKSPACE / 'memory' / 'projects'
    if proj_dir.exists():
        for p in proj_dir.glob('*.md'):
            name = p.stem.replace('-', ' ')
            concepts[name.lower()] = name
    
    # Save index
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(concepts, indent=2, ensure_ascii=False))
    print(f'Concept index: {len(concepts)} concepts')
    return concepts


def load_index():
    """Load or build concept index."""
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text())
    return build_index()


def crosslink(filepath, concepts=None, dry_run=False):
    """Add [[wikilinks]] to a file for known concepts."""
    if concepts is None:
        concepts = load_index()
    
    p = Path(filepath)
    if not p.exists():
        return 0
    
    text = p.read_text()
    original = text
    changes = 0
    
    # Sort concepts by length (longest first) to avoid partial matches
    sorted_concepts = sorted(concepts.items(), key=lambda x: -len(x[0]))
    
    for key, label in sorted_concepts:
        if len(key) < 4:  # skip very short concepts
            continue
        
        # Don't link if already wikilinked
        # Match the concept as a whole word, not inside [[...]] or code blocks
        pattern = re.compile(
            r'(?<!\[\[)(?<!`)(?<!/)\b(' + re.escape(label) + r')\b(?!\]\])(?!`)',
            re.IGNORECASE
        )
        
        def replace_match(m):
            nonlocal changes
            # Don't replace in headings, frontmatter, or code blocks
            start = m.start()
            line_start = text.rfind('\n', 0, start) + 1
            line = text[line_start:text.find('\n', start)]
            if line.strip().startswith('#') or line.strip().startswith('```') or line.strip().startswith('---'):
                return m.group(0)
            changes += 1
            return f'[[{label}]]'
        
        # Only replace first occurrence per concept
        text = pattern.sub(replace_match, text, count=1)
    
    if changes > 0 and not dry_run:
        p.write_text(text)
    
    return changes


if __name__ == '__main__':
    args = sys.argv[1:]
    
    if '--build-index' in args:
        build_index()
    elif '--daily' in args:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        daily_file = DAILY_DIR / f'{today}.md'
        if daily_file.exists():
            concepts = load_index()
            changes = crosslink(daily_file, concepts)
            print(f'{daily_file.name}: {changes} links added')
        else:
            print(f'No daily note for {today}')
    elif '--all-daily' in args:
        concepts = load_index()
        total = 0
        for f in sorted(DAILY_DIR.glob('*.md')):
            c = crosslink(f, concepts)
            if c > 0:
                print(f'  {f.name}: {c} links')
                total += c
        print(f'Total: {total} links across daily notes')
    elif args:
        concepts = load_index()
        changes = crosslink(args[0], concepts)
        print(f'{changes} links added')
    else:
        print(__doc__)
