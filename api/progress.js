// Sync endpoint for Pattern Recall.
//
// The browser cannot talk to MongoDB directly: the driver speaks a binary wire
// protocol over TCP, and Atlas retired its HTTP Data API in September 2025. So
// this small function sits in front of the cluster. The connection string stays
// in the function's environment and is never shipped to the page.
//
// Environment:
//   MONGODB_URI      the Atlas connection string
//   SYNC_KEY         a long random string; the app sends it as a bearer token
//   ALLOWED_ORIGIN   e.g. https://proga97.github.io  (defaults to *)
//   MONGODB_DB       database name (defaults to pattern_recall)
//
// GET  -> the stored state, or null when nothing is stored yet
// PUT  -> replaces the stored state with the posted JSON
'use strict';
const crypto = require('crypto');
const { MongoClient } = require('mongodb');

const DOC_ID = 'me';
let clientPromise = null;

function getDb() {
  if (!clientPromise) {
    // one client per warm lambda, reused across invocations
    clientPromise = new MongoClient(process.env.MONGODB_URI, {
      maxPoolSize: 3,
      serverSelectionTimeoutMS: 8000,
    }).connect();
  }
  return clientPromise.then(c => c.db(process.env.MONGODB_DB || 'pattern_recall'));
}

function keyMatches(given) {
  const want = process.env.SYNC_KEY || '';
  if (!want || !given) return false;
  const a = Buffer.from(given), b = Buffer.from(want);
  if (a.length !== b.length) return false;          // length alone is not secret
  return crypto.timingSafeEqual(a, b);
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', process.env.ALLOWED_ORIGIN || '*');
  res.setHeader('Vary', 'Origin');
  res.setHeader('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');
  res.setHeader('Access-Control-Max-Age', '86400');
  res.setHeader('Cache-Control', 'no-store');

  if (req.method === 'OPTIONS') return res.status(204).end();

  const given = String(req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  if (!keyMatches(given)) return res.status(401).json({ error: 'bad or missing key' });

  try {
    const col = (await getDb()).collection('progress');

    if (req.method === 'GET') {
      const doc = await col.findOne({ _id: DOC_ID });
      return res.status(200).json(doc ? doc.state : null);
    }

    if (req.method === 'PUT') {
      let body = req.body;
      if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = null; } }
      if (!body || typeof body !== 'object' || Array.isArray(body)) {
        return res.status(400).json({ error: 'expected a JSON object' });
      }
      await col.updateOne(
        { _id: DOC_ID },
        { $set: { state: body, updatedAt: new Date() } },
        { upsert: true }
      );
      return res.status(200).json({ ok: true, savedAt: new Date().toISOString() });
    }

    return res.status(405).json({ error: 'use GET or PUT' });
  } catch (e) {
    console.error('progress endpoint failed:', e && e.message);
    return res.status(502).json({ error: 'database unavailable' });
  }
};
