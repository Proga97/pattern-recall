# Setting up MongoDB sync, step by step

This is the whole thing written out, including why each piece exists, so you can
redo it or change it without me.

## The constraint that decides the design

You cannot call MongoDB from a web page. The driver speaks a binary protocol
over a raw TCP socket, and a browser can only speak HTTP. Atlas used to offer an
HTTP Data API that got around this, but MongoDB retired it in September 2025,
along with App Services and Realm.

There is a second reason, and it matters more. A database connection string
contains a username and password. Anything a page can read, every visitor can
read. If the page held the connection string, anyone opening the site would own
your database.

So the shape is fixed:

```
your phone  --HTTPS-->  a small function  --TCP-->  MongoDB Atlas
(GitHub Pages)          (Vercel, holds the secret)   (your data)
```

GitHub Pages stays the host. The function is about eighty lines and exists only
to hold the connection string and check one key. It lives in `api/progress.js`.

## Step 1: make the database

1. Sign up at https://cloud.mongodb.com and create a free **M0** cluster. Any
   region near you is fine.
2. Under **Database Access**, add a user with a password. Write the password
   down. Give it "Read and write to any database".
3. Under **Network Access**, add `0.0.0.0/0`. This feels alarming, and it is the
   normal setting for serverless: Vercel functions get a different IP each time,
   so there is no fixed address to allow. Your password and the sync key are what
   actually protect the data.
4. Press **Connect**, choose **Drivers**, and copy the connection string. It
   looks like `mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/`. Put your
   real password into it where it says `<password>`.

You do not need to create the database or the collection. The first write makes
both.

## Step 2: make a sync key

This is the password the app sends to your endpoint. Generate a long random one:

```bash
openssl rand -hex 32
```

Keep it somewhere you can copy from on your phone, like a password manager.

## Step 3: deploy the endpoint

1. Go to https://vercel.com/new and import `Proga97/pattern-recall`.
2. Framework preset: **Other**. There is nothing to build; Vercel only picks up
   the `api/` folder.
3. Before deploying, open **Environment Variables** and add three:

   | Name | Value |
   |------|-------|
   | `MONGODB_URI` | the connection string from step 1 |
   | `SYNC_KEY` | the random string from step 2 |
   | `ALLOWED_ORIGIN` | `https://proga97.github.io` |

   `ALLOWED_ORIGIN` is the CORS allowance. Browsers refuse cross-site requests
   unless the server names the caller, so this says "the Pages site may call me,
   nothing else may".
4. Deploy. You get a URL like `https://pattern-recall-xxxx.vercel.app`. Your
   endpoint is that plus `/api/progress`.

## Step 4: check it before touching the app

```bash
curl -i https://YOUR-PROJECT.vercel.app/api/progress
```

Expect `401` and `{"error":"bad or missing key"}`. That means it is alive and
refusing strangers. Now with the key:

```bash
curl -H "Authorization: Bearer YOUR_SYNC_KEY" https://YOUR-PROJECT.vercel.app/api/progress
```

Expect `200` and `null`, meaning connected and nothing stored yet. If you get
`502`, the function cannot reach Atlas: check the connection string, the
password, and that Network Access really has `0.0.0.0/0`.

## Step 5: connect the app

On your phone, open https://proga97.github.io/pattern-recall/, then
**Settings**, **Connect a database**. Paste the endpoint address and the sync
key. It should say "synced" within a second.

On your laptop, do the same with the same two values. That is the whole
pairing: same endpoint, same key, same data.

## How the syncing actually works

The rules are in `app/template.html`, in the section marked `remote sync`.

- Every change writes to `localStorage` first and the network second, so the app
  never blocks on a request and keeps working offline.
- Network writes are debounced by 1.5 seconds, so grading ten cards quickly is
  one request, not ten.
- A sync is always **GET, merge, PUT**. It never blindly overwrites.
- The merge is per document. Each card, note, day and drill score carries `_m`,
  the millisecond it was last written. On a conflict the newer one wins.
- Deletes leave a tombstone with a timestamp, so a card you reset on your phone
  does not come back from your laptop's older copy.
- The whole state is one document in Mongo, `progress/me`. At three hundred
  cards it is about 39 KB, against a 16 MB document limit, so there is a lot of
  headroom.

## How I tested it, so you can too

No Atlas account needed. `mongodb-memory-server` downloads a real `mongod` and
runs it in a temp directory.

```bash
mkdir /tmp/mongotest && cd /tmp/mongotest
npm init -y && npm install mongodb mongodb-memory-server
```

Then a script that starts the memory server, sets `MONGODB_URI`, `SYNC_KEY` and
`ALLOWED_ORIGIN`, requires `api/progress.js`, and serves it on a port. Point the
app at `http://localhost:PORT/api/progress`, with `ALLOWED_ORIGIN` set to
wherever you are serving the page from.

The checks worth running: no key gives 401, a wrong key gives 401, `OPTIONS`
gives 204 with the right CORS headers, an empty database gives `null`, a PUT
then GET round trips identically, a non-object body gives 400, and three hundred
cards store without complaint.

The one that actually proves it works: grade a few cards, run
`localStorage.clear()` and reload, reconnect with the same endpoint and key, and
watch the cards, streak and heatmap come back. A cleared browser is
indistinguishable from a new device.

## If something breaks

| Symptom | Cause |
|---------|-------|
| "key rejected" in the app | `SYNC_KEY` in Vercel does not match what you pasted. Redeploy after changing an environment variable, they are read at build time. |
| "endpoint could not reach the database" | Wrong password in `MONGODB_URI`, or Network Access is missing `0.0.0.0/0`. |
| "sync failed" and a CORS error in the console | `ALLOWED_ORIGIN` does not exactly match the site origin. No trailing slash. |
| First request of the day is slow | M0 clusters idle down and cold lambdas reconnect. Normal. |

## The fallback

If you would rather not run any of this, Settings also offers **Use a GitHub
gist**. It keeps the same data in a secret gist on your account, needs no
server, and syncs the same way. The database is the better answer if you want
to query your own history later; the gist is the better answer if you want zero
infrastructure.
