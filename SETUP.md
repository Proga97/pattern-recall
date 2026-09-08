# Setting up sync

Two clicks in the Firebase console. Nothing to do in the app.

## Publishing the rules from the terminal

The console works, but this is one command and cannot be published to the wrong
project, since the project is pinned in `.firebaserc`.

```
npx firebase login
```

```
npx firebase deploy --only firestore:rules
```

The first opens a browser for you to sign in to Google; I cannot do that part.
The second reads `firestore.rules` from this repo and publishes it. Re-run the
second command any time the rules change.

## Step 1: create the database

1. Open the project at https://console.firebase.google.com. It is
   `leet-recall-e4308`, and its config is already in the build.
2. **Build**, **Firestore Database**, **Create database**. Pick a location near
   you; it cannot be changed later.
3. Open the **Rules** tab, paste [firestore.rules](firestore.rules), **Publish**.

## Step 2: there is no step 2

Open https://proga97.github.io/pattern-recall/ on any device and it is already
syncing. No account, no sign-in, no link to copy. Every device that opens the
page reads and writes the same document.

## What the rules do

```
match /users/{userId}  { allow read, write: if true; }
match /tasks/{taskId}  { allow read, write: if true; }
```

`if true` means no condition. Anyone who reaches this database can read and
write those two paths, signed in or not. That is deliberate: it is what removes
every setup step.

The practical consequence, stated plainly so it is never a surprise. The page is
public and its config is in a public repo. Anyone who opens the site shares your
progress: they see your history, and their reviews write into it. Anyone who
finds the project can also delete it. I verified this rather than assuming it:
an unauthenticated request read the document back in full.

If that ever stops being what you want, the fix is small. Ask, and the rules and
app move back to a secret link, which keeps zero setup for you and closes it to
everyone else.

## How the syncing works

The data sits in top level collections, one document per thing:

```
cards/{problemId}     one document per card
notes/{problemId}     one per note you edit
days/{2026-09-08}     one per study day
drill/{pattern-slug}  one per pattern, carrying its display name
extra/{problemId}     problems you added by hand
settings/main
```

- Two devices editing different cards never touch the same document, so neither
  can overwrite the other. A delete is a real delete.
- Every document carries `_m`, the millisecond it was written. On a conflict the
  newer one wins.
- Changes go up as one batched commit, so grading a card is a single round trip
  covering both the card and the day counter.
- A live listener on each collection keeps devices current. This is push, not
  polling.
- Firestore caches offline, so the app works with no connection and queued
  writes go out on reconnect.
- Local storage is written first, so nothing waits on the network. A rejected
  write is retried and nothing is lost.

Pattern names like "Heap / Priority Queue" cannot be document ids because of the
slash, so drill documents are keyed by a slug and carry the real name inside.
Review history is stored as `{t, r}` objects rather than `[t, r]` pairs, because
Firestore rejects an array inside an array.

## If something breaks

| Symptom | Cause |
|---------|-------|
| "Firestore rules are rejecting this" | Step 1.3, rules not published or wrong project. |
| "Cannot reach Firebase right now" | No connection. Nothing is lost, it catches up. |
| Amber dot, "saved on device" | Same. Local storage always has your data. |
| Progress you did not make | Someone else opened the public page. See the rules section. |

Settings has **Stop syncing here**, which leaves this device on local storage
only, and **Use a GitHub gist** as an alternative backend.

## Costs

The free Spark plan covers this easily. A heavy day of studying is a few hundred
reads and writes against a daily allowance in the tens of thousands.
