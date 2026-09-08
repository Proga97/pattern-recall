# Setting up sync, step by step

No account, no password, no sign-in screen. Your progress lives in a Firestore
database on your own Google project, and devices are paired by a private link.

Two console steps, then one tap in the app.

## Step 1: create the database

1. Open your project at https://console.firebase.google.com. It is
   `leet-recall-861a3`, and its config is already baked into the build.
2. **Build**, **Firestore Database**, **Create database**. Pick a location near
   you; it cannot be changed later. Start in **production mode**, which denies
   everything until the rules are in.
3. Open the **Rules** tab, replace what is there with the contents of
   [firestore.rules](firestore.rules) from this repo, and **Publish**.

## Step 2: allow anonymous sign-in

1. **Build**, **Authentication**, **Get started**.
2. In the provider list choose **Anonymous**, enable it, save.

That is the whole auth setup. Anonymous sign-in gives each device a throwaway
session with no identity, no prompt and nothing to remember. You will never see
a login screen. It exists so that every request carries a real Firebase session,
which is what keeps the drive-by scanners out.

You do not need to touch Authorized domains. That list is for OAuth providers
like Google, which this does not use.

## Step 3: turn on sync in the app

Open https://proga97.github.io/pattern-recall/, then **Settings**,
**Connect Firebase**, then **Start syncing on this device**. It shows you a
link. Open that link on your phone and the two devices share the same data from
then on. Nothing to type on the second device.

**Save the link.** It is the only key to your history. Anyone who has it can
read and change your progress, and losing it means losing the data.

## How access is controlled

There are three things standing between your data and a stranger.

1. **A real session.** Every request must be signed in, even anonymously.
   Unauthenticated reads and writes are refused outright, which stops the
   automated scanners that trawl public repos for open Firestore databases.
2. **An unguessable vault id.** Your data sits under 128 random bits generated
   on your first device. That id is what the link carries. It is never committed
   to this repo.
3. **No way to go looking.** Listing vaults is denied, so an id cannot be
   discovered by browsing. The rules also pin the shape: only the six documents
   the app writes, and only the three fields it writes.

I verified all of that against a real Firestore emulator. Seventeen checks:
a second device with a different anonymous session reaches the same vault, a
signed-out request is refused, a short vault id is refused, vaults cannot be
listed, nothing outside the vault is reachable, stray fields and unknown
document names are rejected.

This is the same security model as a secret link. It is weaker than a real login
in one specific way: anyone who gets the link gets in. It is stronger than the
open database you asked about in every way, because that one would let anybody
who found the project id wipe your history.

## How the syncing works

- Each kind of data is its own document under `vaults/<id>/data/`: cards, notes,
  days, drill, extra, settings. Writing one cannot clobber a different change on
  your other device.
- Every card, note, day and drill score carries `_m`, the millisecond it was
  written. Newer wins. Deletes leave a timestamped tombstone so a reset card
  does not come back from an older copy.
- A live listener keeps both devices current, so this is push, not polling.
- Firestore caches offline, so the app works on a train and queued writes go out
  when you reconnect.
- Local storage is written first, so nothing waits on the network.
- If one document is rejected, the others still go, and the failed one retries.

## If something breaks

| Symptom | Cause |
|---------|-------|
| "Turn on Anonymous sign-in..." | Step 2 is not done. |
| "Firestore rules are rejecting this" | Step 1.3. The rules were not published, or the wrong project. |
| Second device shows nothing | Check the whole link was copied, including everything after `#v=`. |
| Amber dot, "saved on device" | No connection. Nothing is lost; it catches up. |
| Lost the link | The data is unreachable. Start syncing again to make a new vault, and the old one just sits there. |

## Costs

The free Spark plan covers this comfortably. A heavy day of studying is a few
hundred reads and writes against a daily allowance in the tens of thousands.

## The alternative

Settings also offers **Use a GitHub gist**, which keeps the same data in a
secret gist with no Google project at all. Same secret-link security model, but
it polls instead of pushing.
