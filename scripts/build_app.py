#!/usr/bin/env python3
"""Merge data/problems.json + data/notes/*.json into app/template.html -> dist/index.html"""
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
problems = json.load(open(ROOT/"data/problems.json"))
notes = {}
for f in sorted(glob.glob(str(ROOT/"data/notes/*.json"))):
    for n in json.load(open(f)):
        notes[n["id"]] = n
missing = [p["id"] for p in problems if p["id"] not in notes]
if missing:
    print("WARNING: no notes for", len(missing), "problems:", missing[:5])
for p in problems:
    n = notes.get(p["id"], {})
    p["patterns"] = n.get("patterns", [])
    p["trigger"] = n.get("trigger", "")
    p["key_idea"] = n.get("key_idea", "")
    p["approach"] = n.get("approach", [])
    p["complexity"] = n.get("complexity", {})
    p["gotcha"] = n.get("gotcha", "")
patterns = [l.strip() for l in open(ROOT/".work/PATTERNS.txt") if l.strip()] if (ROOT/".work/PATTERNS.txt").exists() else []
data = json.dumps({"problems": problems, "patterns": patterns, "built": __import__("datetime").date.today().isoformat()}, ensure_ascii=False)
data = data.replace("</", "<\\/")
tpl = (ROOT/"app/template.html").read_text()
assert "/*__DATA__*/" in tpl
out = tpl.replace("/*__DATA__*/", data)
(ROOT/"dist/index.html").write_text(out)
print(f"dist/index.html: {len(out)//1024} KB, {len(problems)} problems, {len(problems)-len(missing)} with notes")
