#!/usr/bin/env python3
"""Merge data/problems.json + data/notes/*.json into app/template.html -> dist/index.html"""
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
problems = json.load(open(ROOT/"data/problems.json"))
notes = {}
for f in sorted(glob.glob(str(ROOT/"data/notes/chunk_*.json"))):
    for n in json.load(open(f)):
        notes[n["id"]] = n
recog = {}
for f in sorted(glob.glob(str(ROOT/"data/notes/recog_*.json"))):
    for n in json.load(open(f)):
        recog[n["id"]] = n
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
    r = recog.get(p["id"], {})
    p["signals"] = r.get("signals", [])
    p["cread"] = r.get("constraints", "")
    p["confusable"] = r.get("confusable", "")
    p["variants"] = r.get("variants", [])
patterns = [l.strip() for l in open(ROOT/".work/PATTERNS.txt") if l.strip()] if (ROOT/".work/PATTERNS.txt").exists() else []
playbook = json.load(open(ROOT/"data/playbook.json")) if (ROOT/"data/playbook.json").exists() else []
missing_recog = [p["id"] for p in problems if not p.get("signals")]
if missing_recog:
    print("WARNING: no recognition cues for", len(missing_recog), "problems")
data = json.dumps({"problems": problems, "patterns": patterns, "playbook": playbook, "built": __import__("datetime").date.today().isoformat()}, ensure_ascii=False)
data = data.replace("</", "<\\/")
tpl = (ROOT/"app/template.html").read_text()
assert "/*__DATA__*/" in tpl
out = tpl.replace("/*__DATA__*/", data)
(ROOT/"dist/index.html").write_text(out)
# standalone build for GitHub Pages (the Artifact host injects head/viewport; here we write our own)
docs = ROOT / "docs"
docs.mkdir(exist_ok=True)
ICON = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
        "<rect width='64' height='64' rx='14' fill='#2247C9'/>"
        "<rect x='19' y='19' width='26' height='26' rx='6' fill='#fff' transform='rotate(45 32 32)'/></svg>")
head = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">"
        "<meta name=\"theme-color\" content=\"#F4F6F8\" media=\"(prefers-color-scheme: light)\">"
        "<meta name=\"theme-color\" content=\"#0F1218\" media=\"(prefers-color-scheme: dark)\">"
        "<meta name=\"apple-mobile-web-app-capable\" content=\"yes\">"
        "<meta name=\"apple-mobile-web-app-status-bar-style\" content=\"black-translucent\">"
        "<meta name=\"apple-mobile-web-app-title\" content=\"Recall\">"
        "<meta name=\"description\" content=\"Spaced repetition for LeetCode patterns.\">"
        "<link rel=\"manifest\" href=\"manifest.webmanifest\">"
        "<link rel=\"icon\" href=\"icon.svg\" type=\"image/svg+xml\">"
        "<link rel=\"apple-touch-icon\" href=\"icon.png\">"
        "<style>:root{color-scheme:light dark}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>"
        "</head><body>")
sw = ("<script>if('serviceWorker' in navigator){window.addEventListener('load',function(){"
      "navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>")
(docs / "index.html").write_text(head + out + sw + "</body></html>")
(docs / "icon.svg").write_text(ICON)
(docs / "manifest.webmanifest").write_text(json.dumps({
    "name": "Pattern Recall", "short_name": "Recall", "start_url": ".", "scope": ".",
    "display": "standalone", "background_color": "#0F1218", "theme_color": "#0F1218",
    "icons": [{"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
              {"src": "icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, indent=1))
(docs / "sw.js").write_text(
    "// network first, cache fallback: always fresh online, still opens on a train\n"
    "const C='pattern-recall-v1';\n"
    "self.addEventListener('install',e=>self.skipWaiting());\n"
    "self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));\n"
    "self.addEventListener('fetch',function(e){\n"
    "  if(e.request.method!=='GET') return;\n"
    "  const u=new URL(e.request.url);\n"
    "  if(u.origin!==self.location.origin) return;\n"
    "  e.respondWith(fetch(e.request).then(function(r){\n"
    "    const copy=r.clone(); caches.open(C).then(c=>c.put(e.request,copy)); return r;\n"
    "  }).catch(function(){ return caches.match(e.request).then(function(m){ return m || caches.match('index.html'); }); }));\n"
    "});\n")
(docs / ".nojekyll").write_text("")
print("docs/index.html written for GitHub Pages")
print(f"dist/index.html: {len(out)//1024} KB, {len(problems)} problems, "
      f"{len(problems)-len(missing)} with notes, {len(problems)-len(missing_recog)} with cues, "
      f"{len(playbook)} playbook entries")
