/* Rebuild public/all-reads.json from D1 — the dataset the /lab pages render.
 *
 * WHY THIS EXISTS: the file used to be produced by ad-hoc queries typed into a shell, so when a thread was
 * re-read the lab silently kept showing the OLD numbers. Anything the lab draws must be reproducible with one
 * command, or the reference bench stops being a reference.
 *
 *   node tools/build-all-reads.mjs
 *
 * Reads through `wrangler d1 execute --remote`, so it uses the same database the deployed worker writes to and
 * needs no secrets of its own.
 */
import { execFileSync } from "node:child_process";
import fs from "node:fs";

const SYS = ["seek","rage","fear","lust","care","grief","play"];

function q(sql) {
  const out = execFileSync("npx", ["wrangler","d1","execute","m8-social","--remote","--json","--command",sql],
    { encoding:"utf8", maxBuffer: 1 << 28 });
  const m = out.match(/\[\s*\{[\s\S]*\}\s*\]/);
  if (!m) throw new Error("no JSON in wrangler output:\n" + out.slice(0, 400));
  return JSON.parse(m[0])[0].results || [];
}

const tweets = q(`SELECT tweet_id,url,source,text,likes,reply_count,author_handle,agg_json,agg_alt,read_json,created_at
                  FROM tweets WHERE status='done' AND agg_json IS NOT NULL`);

const out = [];
for (const t of tweets) {
  const agg = JSON.parse(t.agg_json || "{}");
  const rows = q(`SELECT likes, read_json FROM comments
                  WHERE tweet_id='${t.tweet_id.replace(/'/g,"''")}' AND read_json IS NOT NULL`);

  // Per-system like sums and one star per commenter per ring. Likes are SPLIT BY SIGNAL SHARE, matching
  // aggregateStats in worker.js and irisFromComments in iris.js: a like endorses the whole comment, and what the
  // comment said is its signals, so a comment firing rage twice and fear once gives rage 2/3 of its likes.
  const weight = {}, stars = {};
  for (const k of SYS) { weight[k] = 0; stars[k] = []; }
  let nread = 0;
  for (const r of rows) {
    let read; try { read = JSON.parse(r.read_json); } catch { continue; }
    const st = read.stats || {};
    const tsig = Object.values(st).reduce((a,v) => a + (v.total || 0), 0);
    if (!tsig) continue;
    nread++;
    for (const k in st) {
      if (!SYS.includes(k)) continue;
      const share = (st[k].total || 0) / tsig, li = Math.max(1, r.likes || 0) * share;   // floor of 1 like: grill item 16
      weight[k] += li;
      stars[k].push(Math.round(li));
    }
  }
  for (const k of SYS) weight[k] = Math.round(weight[k]);

  let post = null, postAlt = 250;
  if (t.read_json) { try { const pr = JSON.parse(t.read_json); post = pr.stats || null;
    postAlt = (pr.altitude && pr.altitude.cal) || 250; } catch {} }

  // created_at = WHEN THE POST WAS MADE. Carried through because the star origin angle is derived from it
  // (grill item 9, decided 2026-07-30): the whole moment, date and time, so every post's eye has its own fixed
  // orientation. Reddit stores this in two formats — raw unix epoch seconds on older rows, ISO-8601 on newer —
  // so whatever consumes it must accept both. See originAngle() in iris.js.
  out.push({ id:t.tweet_id, source:t.source, url:t.url, text:t.text, likes:t.likes||0, author:t.author_handle||'',
             created_at: t.created_at || '',
             agg, weight, stars, post, postAlt, roomAlt: t.agg_alt || 250,
             nread, reported: t.reply_count || nread });
}

// Busiest first, which is the order the lab expects.
out.sort((a,b) => b.nread - a.nread);
fs.writeFileSync("public/all-reads.json", JSON.stringify(out));
console.log(`wrote public/all-reads.json — ${out.length} posts, ${out.reduce((a,r)=>a+r.nread,0)} reads`);
for (const r of out) console.log(`  ${String(r.nread).padStart(4)}c  alt ${String(r.roomAlt).padStart(3)}  ${r.id}`);
