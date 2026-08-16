/* Second rater for the entity coding.
 *
 *   node analysis/deepseek_entity.mjs <shard.json> <out.json> [concurrency]
 *
 * The entity result is the most quotable finding in the paper and, unlike every rate, it has no
 * reliability number beyond 19 of 20 agreement with hand coding on a 20-comment gate. This gives it
 * the same treatment as the affect read: a second model, the same frozen prompt, the same blind
 * shards carrying only id and text.
 *
 * The prompt is read out of instrument/entity-prompt.md rather than restated here, so the two raters
 * cannot drift apart through a copy.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const MODEL = "deepseek-ai/DeepSeek-V3";

const md = fs.readFileSync(path.join(ROOT, "instrument/entity-prompt.md"), "utf8");
const start = md.indexOf("```");
const end = md.indexOf("```", start + 3);
if (start < 0 || end < 0) throw new Error("prompt block not found in entity-prompt.md");
const TEMPLATE = md.slice(start + 3, end).replace(/^\n/, "");
if (!TEMPLATE.includes("<TEXT>")) throw new Error("prompt block has no <TEXT> placeholder");

const env = Object.fromEntries(
  fs.readFileSync(path.join(process.env.HOME, "the instrument repository/.dev.vars"), "utf8")
    .split("\n").filter(l => l.includes("=") && !l.trim().startsWith("#"))
    .map(l => [l.slice(0, l.indexOf("=")).trim(), l.slice(l.indexOf("=") + 1).trim()]));

const LABELS = new Set(["model", "instance", "persona", "unspecified", "none"]);

async function codeOne(c, tries = 3) {
  const prompt = TEMPLATE.replace("<TEXT>", c.text);
  for (let t = 0; t < tries; t++) {
    try {
      const r = await fetch("https://api.deepinfra.com/v1/openai/chat/completions", {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${env.DEEPINFRA_API_KEY}` },
        body: JSON.stringify({ model: MODEL, temperature: 0, max_tokens: 600,
                               messages: [{ role: "user", content: prompt }] }),
      });
      if (!r.ok) { await new Promise(s => setTimeout(s, 1200 * (t + 1))); continue; }
      const j = await r.json();
      const m = (j?.choices?.[0]?.message?.content || "").match(/\{[\s\S]*\}/);
      if (!m) continue;
      const d = JSON.parse(m[0]);
      const label = LABELS.has(d.label) ? d.label : null;
      if (!label) continue;   // an out-of-vocabulary label is dropped, never repaired
      return { id: c.id, label, secondary: d.secondary ?? null, evidence: d.evidence ?? "" };
    } catch { await new Promise(s => setTimeout(s, 1200 * (t + 1))); }
  }
  return { id: c.id, label: null, failed: true };
}

const [, , shardPath, outPath, conc = "8"] = process.argv;
const shard = JSON.parse(fs.readFileSync(shardPath, "utf8"));
const out = new Array(shard.length);
let next = 0;
await Promise.all(Array.from({ length: Number(conc) }, async () => {
  while (true) {
    const i = next++;
    if (i >= shard.length) return;
    out[i] = await codeOne(shard[i]);
  }
}));
fs.writeFileSync(outPath, JSON.stringify(out, null, 1));
console.log(`${outPath} ${out.length} coded, ${out.filter(r => r.failed).length} failed`);
