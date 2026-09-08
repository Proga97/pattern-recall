# Setting up Firebase sync, step by step

Your review history lives in a Firestore database on your own Google account.
Every device that signs in with that account sees the same data, and changes
appear on the other device within a second without a refresh.

There is no server to deploy and no key to paste. The Firebase config the page
holds is public by design; what actually protects your data is the security
rules in `firestore.rules`.

## Step 1: create the project

Already done. The project is `leet-recall-861a3` and its config is baked into
the build in `data/firebase.json`, so no device has to paste anything.

That config is not a secret. It identifies the project, it does not grant
access, and Firebase publishes it in every web app it generates. If you ever
want a second layer, restrict the API key to your domain in the Google Cloud
console under APIs and Services, Credentials, HTTP referrers.

To point the app at a different project instead, replace `data/firebase.json`
and rebuild, or paste another config under "Use a different project" in the
Connect Firebase sheet.

## Step 2: create the database

1. In the left sidebar, **Build**, **Firestore Database**, **Create database**.
2. Pick a location near you. This cannot be changed later.
3. Start in **production mode**. That denies everything by default, which is
   what you want before the rules are in.
4. Open the **Rules** tab, delete what is there, paste the contents of
   [firestore.rules](firestore.rules) from this repo, and click **Publish**.

Those rules say one thing: a signed-in account may read and write documents
under its own user id, and nothing else in the database is reachable by anyone.
I tested them against the Firestore emulator, thirteen checks covering another
account reading your data, a signed-out visitor reading or writing, and writes
outside the user tree. All denied.

## Step 3: turn on sign-in

1. **Build**, **Authentication**, **Get started**.
2. Choose **Google** in the provider list, enable it, pick a support email,
   and save.
3. Still in Authentication, open **Settings**, then **Authorized domains**, and
   add `proga97.github.io`. Sign-in is refused from any domain not on that list.

## Step 4: connect the app

Open https://proga97.github.io/pattern-recall/ then **Settings**,
**Connect Firebase**, and press **Sign in with Google**. The project is already
filled in, so there is nothing to paste.

On your other device, do the same. Same Google account means the same data.

## How the syncing works

- Each kind of data is its own document under `users/<your id>/data/`: cards,
  notes, days, drill, extra, settings. Writing one cannot clobber a different
  change on your other device.
- Every card, note, day and drill score carries `_m`, the millisecond it was
  last written. On a conflict the newer one wins. Deletes leave a tombstone with
  a timestamp so a reset card does not come back from an older copy.
- A live listener keeps both devices current, so this is push, not polling.
- Firestore keeps an offline cache, so the app works on a train and the queued
  writes go out when you reconnect.
- Local storage is still written first, so nothing depends on the network.

## If something breaks

| Symptom | Cause |
|---------|-------|
| "This site is not in the Firebase authorized domains list" | Step 3.3. Add `proga97.github.io` exactly, no `https://`. |
| "rules deny access" | The rules were not published, or were pasted into the wrong project. |
| "Missing or insufficient permissions" in the console | Same as above. The rules tab should show the `users/{uid}/data/{docId}` block. |
| The popup closes and nothing happens | Some browsers and installed apps block popups. The app falls back to a full-page redirect on its own; let it. |
| Works on one device, not the other | Check you signed in with the same Google account. Different accounts get different user ids and therefore different data. |

## Costs

The free Spark plan covers this comfortably. A day of heavy studying is a few
hundred reads and writes against a daily allowance in the tens of thousands.

## The alternative

Settings also offers **Use a GitHub gist**, which keeps the same data in a
secret gist on your GitHub account with no Google involvement and no project to
create. It polls instead of pushing, so cross-device updates take a few seconds
rather than being instant.

## What was removed

An earlier version synced through MongoDB Atlas with a small Vercel function in
front, because a browser cannot speak MongoDB's wire protocol. Firestore talks
to the browser directly, so that server piece is gone. It is still in the git
history if you ever want it back.
