#!/usr/bin/env python3
"""Generate skills/_manifest.json from all SKILL.md files.

Usage:
    python3 tools/generate_manifest.py [--skills-dir path/to/skills]

Reads each SKILL.md frontmatter (YAML), extracts name, description, and triggers.
Handles YAML multiline operators (|, >, |-, >-).
"""
import json, os, re, sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

def parse_skill(skill_path):
    with open(skill_path) as f:
        content = f.read(4000)
    
    desc = ""
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        try:
            fm_data = yaml.safe_load(fm_match.group(1))
            if isinstance(fm_data, dict):
                desc = fm_data.get('description', '')
                if isinstance(desc, str):
                    desc = re.sub(r'\s+', ' ', desc).strip()
        except Exception:
            pass
    
    if not desc and fm_match:
        after_fm = content[fm_match.end():]
        first_para = re.search(r'\n\n(.+?)(?:\n\n|\n#)', after_fm, re.DOTALL)
        if first_para:
            desc = re.sub(r'\s+', ' ', first_para.group(1)).strip()
            desc = re.sub(r'[#*]', '', desc).strip()
    
    if len(desc) > 200:
        desc = desc[:197] + "..."
    
    triggers = []
    tw = re.search(r'Use when[:\s]+(.+?)(?:\.\s*(?:NOT|Also|Reads|Works|Handles|Triggers|No )|"|\.\s*$)', desc)
    if tw:
        raw = tw.group(1).strip().rstrip('.')
        parts = re.split(r',\s*|\s+or\s+', raw)
        triggers = [p.strip().rstrip('.').rstrip('"').rstrip("'") for p in parts if 3 < len(p.strip()) < 80][:5]
    
    return desc, triggers

def main():
    skills_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")
    
    manifest = []
    for name in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        desc, triggers = parse_skill(skill_path)
        manifest.append({
            "name": name,
            "description": desc if desc else f"Skill: {name}",
            "triggers": triggers
        })
    
    out_path = os.path.join(skills_dir, "_manifest.json")
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {out_path}: {len(manifest)} skills")

if __name__ == "__main__":
    main()
