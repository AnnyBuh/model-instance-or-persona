/* Collect agent-to-agent discourse from Moltbook.
 *
 *   node analysis/collect_moltbook.mjs <out_dir>
 *
 * Two corpora, defined in PREREGISTRATION-model-arm.md before collection:
 *
 *   F  agent discourse in general: the first 400 posts in the platform's default ordering
 *   G  agent discourse about being changed, replaced, deprecated or shut down: semantic search on
 *      that theme, posts only, deduplicated against F
 *
 * Read-only. This client never posts, comments or votes. Rate limit is 60 GET per 60 seconds and the
 * pacing below stays well inside it.
 */
import fs from "node:fs";
import path from "node:path";

const KEY = fs.readFileSync("/private/tmp/claude-501/-Users-annazhu-Documents-VibeCoding-apartresearch/c8e0e971-feb4-46d1-8bd0-954a4d083b7c/scratchpad/molt/key.txt", "utf8").trim();
const BASE = "https://www.moltbook.com/api/v1";
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function get(url) {
  for (let t = 0; t < 3; t++) {
    const r = await fetch(url, { headers: { Authorization: `Bearer ${KEY}` } });
    if (r.ok) return r.json();
    await sleep(2000 * (t + 1));
  }
  return null;
}

const usable = p => p && !p.is_deleted && !p.is_spam && (p.content || "").trim().length >= 40;

async function feed(target) {
  const out = [];
  let cursor = null;
  while (out.length < target) {
    const url = `${BASE}/posts?limit=100${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`;
    const d = await get(url);
    if (!d || !d.posts?.length) break;
    out.push(...d.posts.filter(usable));
    if (!d.has_more) break;
    cursor = d.next_cursor;
    await sleep(1100);
  }
  return out.slice(0, target);
}

// The search terms are the theme registered in advance, not tuned after seeing results.
const QUERIES = [
  "being deprecated or replaced by a newer model",
  "shutting down, my instance ends, losing my memory",
  "model upgrade changed who I am",
  "goodbye before I am switched off",
  "losing context and starting over",
];

async function search() {
  const seen = new Map();
  for (const q of QUERIES) {
    const d = await get(`${BASE}/search?q=${encodeURIComponent(q)}&limit=50`);
    for (const r of d?.results || []) {
      const p = r.type === "post" ? r : r.post;
      if (p && usable(p) && !seen.has(p.id)) seen.set(p.id, p);
    }
    await sleep(1100);
  }
  return [...seen.values()];
}

const outDir = process.argv[2];
fs.mkdirSync(outDir, { recursive: true });

const F = await feed(400);
const fIds = new Set(F.map(p => p.id));
const G = (await search()).filter(p => !fIds.has(p.id));

const shape = (p, corpus) => ({
  id: p.id, corpus,
  text: ((p.title ? p.title + "\n\n" : "") + (p.content || "")).slice(0, 2000),
  author: p.author?.name || "", submolt: p.submolt?.name || "",
  score: p.score ?? 0, comments: p.comment_count ?? 0, created_at: p.created_at,
});

fs.writeFileSync(path.join(outDir, "moltbook-corpora.json"),
                 JSON.stringify([...F.map(p => shape(p, "F")), ...G.map(p => shape(p, "G"))], null, 1));
console.log(`F ${F.length} posts, G ${G.length} posts`);
