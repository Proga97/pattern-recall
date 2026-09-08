# Pattern Recall

Spaced repetition for the LeetCode problems in
[Proga97/leetcode_dump](https://github.com/Proga97/leetcode_dump), built for
recognising patterns in problems you have *not* seen before.

**Open it:** https://proga97.github.io/pattern-recall/

Every card asks for the pattern and the key idea before it shows anything.
The back gives you the signals that should have fired, what the constraint
sizes imply, the approach, the pattern it is easy to confuse with, and your
own accepted solution.

## What is in it

- **Today** — due count, new count, streak, a twelve week heatmap, weakest patterns.
- **Review** — the spaced repetition queue, SM-2 with Anki style buttons.
- **Spot the pattern** — a fast multiple choice drill on problem statements, weighted towards your weak patterns. This is the part that trains you for unseen problems.
- **Library** — every problem and every pattern, with mastery bars.
- **Playbook** — a constraint-size to complexity table, a phrase to pattern map, an opening checklist, and a code template plus classic bugs for each of 34 patterns.

## Where your progress lives

Nothing runs on a server. The page is one static HTML file.

Progress syncs through a **secret gist on your own GitHub account**. On the
first device, Settings then Connect GitHub, paste a fine-grained token with
only the Gists permission, and the page creates the gist. On the next device,
paste the same token plus the gist id. The token is kept in that browser's
local storage and is sent only to `api.github.com`.

Writes go to local storage first and the gist second, so the app keeps working
offline and catches up later. Merges are per document, newest write wins, with
tombstones so a delete on one device does not come back from another.

If you never connect GitHub, everything still works and stays on one device.

## Building it yourself

```
python3 scripts/build_problems.py    # clone/pull the dump -> data/problems.json
python3 scripts/build_app.py         # -> docs/ and dist/
```

Then open `docs/index.html` through any static server. Opening the file
directly works too, but a `file://` page gets no service worker.

## Layout

| Path | What |
|------|------|
| `scripts/build_problems.py` | Clones or pulls the dump, writes `data/problems.json`. |
| `data/notes/chunk_*.json` | Pattern, trigger, key idea, approach, complexity, gotcha. |
| `data/notes/recog_*.json` | Signals, constraint reading, confusable with, variants. |
| `data/playbook.json` | The 34 pattern templates. |
| `app/template.html` | App source, no framework, no build step. |
| `scripts/build_app.py` | Merges data into the template, writes `docs/` and `dist/`. |
| `docs/` | Generated. Built by CI and uploaded to Pages. Not in git. |
| `dist/index.html` | Generated. The same page as a Claude Artifact fragment. Not in git. |

## Adding new solves

A nightly GitHub Action pulls the dump, rebuilds, and deploys to Pages, so new
problems appear in the deck on their own. They arrive without notes, showing as
untagged. To write notes for them, ask Claude Code
**"sync my leetcode deck"** in this repo, or fill them in from the app:
Library, open the problem, Edit.

## Scheduler

New and learning cards: Again and Hard repeat in ten minutes, Good graduates to
one day, Easy to four days. Review cards: Again lapses, ease minus 0.2, interval
times 0.4. Hard times 1.2 with ease minus 0.15. Good times ease. Easy times ease
times 1.3 with ease plus 0.15. Ease starts at 2.5 and floors at 1.3.
