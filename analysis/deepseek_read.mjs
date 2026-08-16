/* Second rater: read the same corpora with DeepSeek-V3, for a replication check.
 *
 *   node analysis/deepseek_read.mjs <shard.json> <out.reads.json> [concurrency]
 *
 * Why this exists. Every number in the study comes from one rater. The obvious objection is that the
 * finding is a property of that rater rather than of the corpora. A second model reading the same
 * comments under the SAME frozen prompt answers it directly: if the placement replicates, it is not
 * the rater.
 *
 * Why it does NOT go through the worker. Making the worker read these threads means setting a read
 * limit, which flips them to status='done', which fires publishGallery() and puts grief and AI-loss
 * threads on a public website. That is the exact thing we gated out. So this calls DeepInfra directly
 * against the exported shards: no worker, no D1 writes, no gallery.
 *
 * The prompt is extracted verbatim from the same reference file the human-side reads used, so the two
 * raters are answering the identical question. Do not edit it here.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const MODEL = "deepseek-ai/DeepSeek-V3";

// the frozen prompt, lifted from the reference copy rather than reimplemented
const src = fs.readFileSync(path.join(ROOT, "instrument/read-prompt.reference.js"), "utf8");
const need = ["const CHARGES =", "const POLES =", "const JSON_RULE =", "const HAWKINS_LEVELS", "function tweetReadPrompt"];
let code = "";
for (const marker of need) {
  const i = src.indexOf(marker);
  if (i < 0) throw new Error("not found in reference prompt: " + marker);
  const rest = src.slice(i);
  const end = marker.startsWith("function") ? rest.indexOf("\n}\n") + 3 : rest.indexOf(";\n") + 2;
  code += rest.slice(0, end) + "\n";
}
const { tweetReadPrompt } = new Function(code + "\nreturn { tweetReadPrompt };")();

// DEEPINFRA_API_KEY comes from the environment. Set it directly, or point INSTRUMENT_ENV_FILE
// at a dotenv file holding it, so no local path is baked into a published script.
const env = (() => {
  if (process.env.DEEPINFRA_API_KEY) return { DEEPINFRA_API_KEY: process.env.DEEPINFRA_API_KEY };
  const f = process.env.INSTRUMENT_ENV_FILE;
  if (!f) throw new Error("set DEEPINFRA_API_KEY or INSTRUMENT_ENV_FILE");
  return Object.fromEntries(fs.readFileSync(f, "utf8").split("\n")
    .filter(l => l.includes("=") && !l.trim().startsWith("#"))
    .map(l => [l.slice(0, l.indexOf("=")).trim(), l.slice(l.indexOf("=") + 1).trim()]));
})();

const SYSTEMS = new Set(["seeking", "rage", "fear", "lust", "care", "grief", "play"]);
const BANDS = new Set(["above", "shutdown", "overwhelm"]);

async function readOne(c, tries = 3) {
  for (let t = 0; t < tries; t++) {
    try {
      const r = await fetch("https://api.deepinfra.com/v1/openai/chat/completions", {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${env.DEEPINFRA_API_KEY}` },
        body: JSON.stringify({
          model: MODEL, temperature: 0, max_tokens: 5000,
          messages: [{ role: "user", content: tweetReadPrompt(c.text, c.post || "") }],
        }),
      });
      if (!r.ok) { await new Promise(s => setTimeout(s, 1500 * (t + 1))); continue; }
      const j = await r.json();
      const m = (j?.choices?.[0]?.message?.content || "").match(/\{[\s\S]*\}/);
      if (!m) continue;
      const d = JSON.parse(m[0]);
      // keep the same validity rule as the main analysis: drop labels outside the seven, never repair
      const segments = (d.segments || []).map(s => ({
        ...s, systems: (s.systems || []).filter(f => SYSTEMS.has(f?.system) && BANDS.has(f?.band)),
      }));
      const alt = typeof d.altitude === "object" ? (d.altitude?.level || null) : (d.altitude || null);
      return { id: c.id, altitude: alt, segments };
    } catch { await new Promise(s => setTimeout(s, 1500 * (t + 1))); }
  }
  return { id: c.id, altitude: null, segments: [], failed: true };
}

const [, , shardPath, outPath, conc = "8"] = process.argv;
const shard = JSON.parse(fs.readFileSync(shardPath, "utf8"));
const out = new Array(shard.length);
let next = 0, done = 0;
const workers = Array.from({ length: Number(conc) }, async () => {
  while (true) {
    const i = next++;
    if (i >= shard.length) return;
    out[i] = await readOne(shard[i]);
    if (++done % 25 === 0) process.stderr.write(`  ${done}/${shard.length}\n`);
  }
});
await Promise.all(workers);
fs.writeFileSync(outPath, JSON.stringify(out, null, 1));
const failed = out.filter(r => r.failed).length;
console.log(`${outPath} ${out.length} reads, ${failed} failed`);
