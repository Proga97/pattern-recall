# Pattern Recall

Anki-style spaced repetition for the LeetCode problems in
[Proga97/leetcode_dump](https://github.com/Proga97/leetcode_dump).
Each card asks for the *pattern* and *key idea* first, then reveals the
trigger, approach steps, complexity, gotcha, and your own solution.

The app is a single HTML page published as a claude.ai Artifact. Review
progress lives in the artifact's cloud database, so it syncs across
phone and laptop as long as you open it from claude.ai.

Live artifact: https://claude.ai/code/artifact/a1fb7f68-abec-4801-9f89-3b519d9da4b2

## Layout

| Path | What |
|------|------|
| `scripts/build_problems.py` | Clones/pulls the dump and writes `data/problems.json` (title, difficulty, statement, your code, first-solve date). |
| `data/notes/*.json` | Pattern notes per problem (patterns, trigger, key idea, approach, complexity, gotcha). Generated once, hand-editable. |
| `scripts/build_app.py` | Merges problems + notes into `app/template.html` and writes `dist/index.html`. |
| `app/template.html` | The app source (CSS + JS, no framework). |
| `dist/index.html` | Built page, the thing that gets published. |

## Syncing new problems

Ask Claude Code: **"sync my leetcode deck"**. It will run:

```bash
python3 scripts/build_problems.py
python3 scripts/build_app.py
```

then write notes for any problem that has no entry in `data/notes/`, and
republish the artifact at the same URL. Progress is untouched by a
republish. Problems can also be added by hand from the app's Library tab.

## Scheduler

SM-2 with Anki-style buttons. New/learning cards: Again or Hard repeat in
10 minutes, Good graduates to 1 day, Easy to 4 days. Review cards: Again
lapses (ease -0.2, interval x0.4, relearn), Hard x1.2 (ease -0.15),
Good x ease, Easy x ease x1.3 (ease +0.15). Ease floor 1.3, start 2.5.
Daily new-card limit and introduction order are in Settings.
