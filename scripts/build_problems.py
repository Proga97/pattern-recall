#!/usr/bin/env python3
"""Build data/problems.json from the leetcode_dump repo (LeetHub layout).

Usage: python3 scripts/build_problems.py [path-to-leetcode_dump-clone]
If no path is given the dump is cloned/pulled into .cache/leetcode_dump.
"""
import html, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUMP_URL = "https://github.com/Proga97/leetcode_dump.git"
OUT = ROOT / "data" / "problems.json"

def get_dump(arg):
    if arg:
        return Path(arg)
    d = ROOT / ".cache" / "leetcode_dump"
    if d.exists():
        subprocess.run(["git", "-C", str(d), "pull", "-q"], check=True)
    else:
        d.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-q", DUMP_URL, str(d)], check=True)
    return d

def first_commit_date(dump, rel):
    out = subprocess.run(["git", "-C", str(dump), "log", "--diff-filter=A", "--follow",
                          "--format=%aI", "--", rel], capture_output=True, text=True).stdout
    lines = [l for l in out.splitlines() if l.strip()]
    return lines[-1][:10] if lines else None

def last_commit_date(dump, rel):
    out = subprocess.run(["git", "-C", str(dump), "log", "-1", "--format=%aI", "--", rel],
                         capture_output=True, text=True).stdout.strip()
    return out[:10] if out else None

HEAD_RE = re.compile(r'<h2><a href="([^"]+)">(\d+)\.\s*(.*?)</a></h2><h3>(Easy|Medium|Hard)</h3><hr>', re.S)

def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def parse(dump):
    problems = []
    for d in sorted(p for p in dump.iterdir() if p.is_dir() and not p.name.startswith(".")):
        readme = d / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text(encoding="utf-8")
        m = HEAD_RE.search(text)
        if not m:
            print("skip (no header):", d.name, file=sys.stderr)
            continue
        url, num, title, diff = m.groups()
        body = text[m.end():].strip()
        # short statement = text up to the first example
        short = strip_tags(body.split('<strong class="example">')[0])
        short = short.replace(" ", " ").strip()
        code_files = [f for f in d.iterdir() if f.is_file() and f.name != "README.md"]
        code, lang = "", ""
        if code_files:
            cf = sorted(code_files)[0]
            lang = cf.suffix.lstrip(".")
            code = cf.read_text(encoding="utf-8", errors="replace")
            code = re.sub(r"\n*# Synced seamlessly with LeetHub.*$", "", code, flags=re.S).rstrip() + "\n"
        slug = d.name
        problems.append({
            "id": slug,
            "num": int(num),
            "title": html.unescape(title).strip(),
            "difficulty": diff,
            "url": url.rstrip("/"),
            "short": short[:600],
            "description_html": body,
            "code": code,
            "lang": lang,
            "solved_at": first_commit_date(dump, f"{slug}/README.md") or last_commit_date(dump, slug),
        })
    return problems

if __name__ == "__main__":
    dump = get_dump(sys.argv[1] if len(sys.argv) > 1 else None)
    probs = parse(dump)
    OUT.write_text(json.dumps(probs, indent=1, ensure_ascii=False))
    print(f"wrote {len(probs)} problems -> {OUT}")
