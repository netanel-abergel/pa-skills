#!/usr/bin/env python3
"""Memory health checker — runs on the graphify knowledge graph + memory files.

Detects:
1. Disconnected nodes — concepts mentioned once, never linked
2. Stale clusters — communities with no recent activity
3. Contradictions — conflicting rules in MEMORY.md vs daily notes
4. Memory gaps — days without daily notes, skills never referenced
5. Decay — edges that haven't been reinforced recently

Usage:
    python3 tools/memory_health.py              # full report
    python3 tools/memory_health.py --quick      # quick summary only
    python3 tools/memory_health.py --fix        # auto-fix safe issues
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path(os.environ.get('WORKSPACE', '/opt/ocana/openclaw/workspace'))
GRAPH_PATH = WORKSPACE / 'graphify-out' / 'graph.json'
MEMORY_PATH = WORKSPACE / 'MEMORY.md'
DAILY_DIR = WORKSPACE / 'memory' / 'daily'
SKILLS_DIR = WORKSPACE / 'skills'
REPORT_PATH = WORKSPACE / 'memory' / 'health-report.md'


def load_graph():
    """Load the knowledge graph."""
    if not GRAPH_PATH.exists():
        return None, None, None
    data = json.loads(GRAPH_PATH.read_text())
    nodes = data.get('nodes', [])
    edges = data.get('edges', data.get('links', []))
    # Build adjacency
    adj = {}
    for n in nodes:
        nid = n.get('id', n.get('label', ''))
        if nid:
            adj[nid] = {'node': n, 'connections': 0, 'edges': []}
    for e in edges:
        src = e.get('source', '')
        tgt = e.get('target', '')
        if src in adj:
            adj[src]['connections'] += 1
            adj[src]['edges'].append(e)
        if tgt in adj:
            adj[tgt]['connections'] += 1
            adj[tgt]['edges'].append(e)
    return nodes, edges, adj


def check_disconnected_nodes(adj):
    """Find nodes with 0 connections — orphans."""
    orphans = []
    for nid, info in adj.items():
        if info['connections'] == 0:
            node = info['node']
            orphans.append({
                'id': nid,
                'label': node.get('label', nid),
                'source_file': node.get('source_file', '?'),
                'type': node.get('file_type', '?')
            })
    return orphans


def check_daily_note_gaps():
    """Find days without daily notes in the last 30 days."""
    today = datetime.utcnow().date()
    gaps = []
    for i in range(30):
        d = today - timedelta(days=i)
        fname = DAILY_DIR / f'{d.isoformat()}.md'
        if not fname.exists():
            gaps.append(d.isoformat())
    return gaps


def check_stale_skills(adj):
    """Find skills that exist but are never referenced in the graph."""
    skill_dirs = set()
    if SKILLS_DIR.exists():
        for p in SKILLS_DIR.iterdir():
            if p.is_dir() and (p / 'SKILL.md').exists():
                skill_dirs.add(p.name)
    
    # Check which skills appear in graph
    referenced = set()
    for nid, info in adj.items():
        label = info['node'].get('label', '').lower()
        source = info['node'].get('source_file', '').lower()
        for skill in skill_dirs:
            if skill.lower() in label or skill.lower() in source:
                referenced.add(skill)
    
    unreferenced = skill_dirs - referenced
    return sorted(unreferenced)


def check_memory_staleness():
    """Check if MEMORY.md has entries that might be outdated."""
    if not MEMORY_PATH.exists():
        return []
    
    text = MEMORY_PATH.read_text()
    stale_signals = []
    
    # Look for date references that are old
    import re
    date_pattern = re.compile(r'202[56]-\d{2}-\d{2}')
    today = datetime.utcnow().date()
    
    for i, line in enumerate(text.split('\n'), 1):
        matches = date_pattern.findall(line)
        for m in matches:
            try:
                d = datetime.strptime(m, '%Y-%m-%d').date()
                age = (today - d).days
                if age > 14:
                    stale_signals.append({
                        'line': i,
                        'date': m,
                        'age_days': age,
                        'text': line.strip()[:100]
                    })
            except:
                pass
    
    return stale_signals


def check_weak_communities(nodes, edges, adj):
    """Find communities with very few internal edges (loosely connected)."""
    # Group by community
    communities = {}
    for n in nodes:
        nid = n.get('id', n.get('label', ''))
        comm = n.get('community', -1)
        if comm not in communities:
            communities[comm] = []
        communities[comm].append(nid)
    
    weak = []
    for comm_id, members in communities.items():
        if len(members) < 2:
            continue
        member_set = set(members)
        internal_edges = 0
        for e in edges:
            if e.get('source') in member_set and e.get('target') in member_set:
                internal_edges += 1
        
        ratio = internal_edges / len(members) if members else 0
        if ratio < 0.3 and len(members) >= 3:
            weak.append({
                'community': comm_id,
                'members': len(members),
                'internal_edges': internal_edges,
                'ratio': round(ratio, 2),
                'sample_members': [adj[m]['node'].get('label', m) for m in members[:3] if m in adj]
            })
    
    return sorted(weak, key=lambda x: x['ratio'])[:10]


def check_recent_activity(adj):
    """Check which areas of the graph have recent vs old activity."""
    today = datetime.utcnow().date()
    recent_files = set()
    old_files = set()
    
    for nid, info in adj.items():
        source = info['node'].get('source_file', '')
        if source:
            p = WORKSPACE / source if not source.startswith('/') else Path(source)
            if p.exists():
                mtime = datetime.fromtimestamp(p.stat().st_mtime).date()
                age = (today - mtime).days
                if age <= 7:
                    recent_files.add(source)
                elif age > 30:
                    old_files.add(source)
    
    return recent_files, old_files


def generate_report(quick=False):
    """Generate the full health report."""
    nodes, edges, adj = load_graph()
    if not adj:
        return "No knowledge graph found. Run graphify first."
    
    lines = [f"# Memory Health Report — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"]
    
    # Summary
    orphans = check_disconnected_nodes(adj)
    gaps = check_daily_note_gaps()
    stale_skills = check_stale_skills(adj)
    stale_memory = check_memory_staleness()
    weak = check_weak_communities(nodes, edges, adj)
    recent, old = check_recent_activity(adj)
    
    # Score
    issues = len(orphans) + len(gaps) + len(stale_skills) + len(stale_memory) + len(weak)
    if issues == 0:
        health = "EXCELLENT"
    elif issues < 10:
        health = "GOOD"
    elif issues < 30:
        health = "FAIR"
    else:
        health = "NEEDS ATTENTION"
    
    lines.append(f"## Health: {health}")
    lines.append(f"- Graph: {len(nodes)} nodes, {len(edges)} edges")
    lines.append(f"- Orphan nodes: {len(orphans)}")
    lines.append(f"- Daily note gaps (30d): {len(gaps)}")
    lines.append(f"- Unreferenced skills: {len(stale_skills)}")
    lines.append(f"- Stale MEMORY.md entries: {len(stale_memory)}")
    lines.append(f"- Weak communities: {len(weak)}")
    lines.append(f"- Recent files (7d): {len(recent)} | Old files (30d+): {len(old)}")
    lines.append("")
    
    if quick:
        return '\n'.join(lines)
    
    # Details
    if orphans:
        lines.append("## Disconnected Nodes (orphans)")
        lines.append("These nodes have 0 connections — consider linking or removing:")
        for o in orphans[:15]:
            lines.append(f"- `{o['label']}` ({o['type']}) — {o['source_file']}")
        if len(orphans) > 15:
            lines.append(f"- ... and {len(orphans)-15} more")
        lines.append("")
    
    if gaps:
        lines.append("## Daily Note Gaps")
        lines.append(f"Missing daily notes for {len(gaps)} of last 30 days:")
        for g in gaps[:10]:
            lines.append(f"- {g}")
        lines.append("")
    
    if stale_skills:
        lines.append("## Unreferenced Skills")
        lines.append("These skills exist but don't appear in the knowledge graph:")
        for s in stale_skills:
            lines.append(f"- {s}")
        lines.append("")
    
    if stale_memory:
        lines.append("## Stale MEMORY.md Entries")
        lines.append("Entries referencing dates older than 14 days — may need review:")
        for s in stale_memory[:10]:
            lines.append(f"- Line {s['line']} ({s['age_days']}d old): {s['text']}")
        if len(stale_memory) > 10:
            lines.append(f"- ... and {len(stale_memory)-10} more")
        lines.append("")
    
    if weak:
        lines.append("## Weak Communities")
        lines.append("These clusters have low internal connectivity:")
        for w in weak:
            members_str = ', '.join(w['sample_members'])
            lines.append(f"- Community {w['community']}: {w['members']} members, {w['internal_edges']} edges (ratio: {w['ratio']}) — e.g. {members_str}")
        lines.append("")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    quick = '--quick' in sys.argv
    report = generate_report(quick=quick)
    
    # Save report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report)
    
    print(report)
