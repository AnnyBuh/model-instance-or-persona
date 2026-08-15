/* How OFTEN does a rule fire? At temperature 0 this model still differs on ~20% of comments between runs, so a
 * single read proves nothing. This runs each case N times under a candidate prompt and reports the RATE at which
 * each system appears — the only honest way to compare two prompts on a handful of cases.
 *
 *   node tools/rate.mjs <cases.json> <worker.js> <repeats>
 */
import fs from "node:fs";
const src = fs.readFileSync(process.argv[3], "utf8");
const need = ["const POLES =", "const CHARGES =", "const JSON_RULE =", "const HAWKINS =",
              "const HAWKINS_LEVELS", "function tweetReadPrompt"];
let code = "";
for (const marker of need) {
  const i = src.indexOf(marker); if (i < 0) throw new Error("not found: " + marker);
  const rest = src.slice(i);
  const end = marker.startsWith("function") ? rest.indexOf("\n}\n") + 3 : rest.indexOf(";\n") + 2;
  code += rest.slice(0, end) + "\n";
}
const { tweetReadPrompt } = new Function(code + "\nreturn { tweetReadPrompt };")();
const env = Object.fromEntries(fs.readFileSync(new URL("../.dev.vars", import.meta.url), "utf8")
  .split("\n").filter(l => l.includes("=") && !l.trim().startsWith("#"))
  .map(l => [l.slice(0, l.indexOf("=")).trim(), l.slice(l.indexOf("=") + 1).trim().replace(/^["']|["']$/g, "")]));
const { post, cases } = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const N = parseInt(process.argv[4], 10) || 5;
const model = "deepseek-ai/DeepSeek-V3";

const one = async (text) => {
  const r = await fetch("https://api.deepinfra.com/v1/openai/chat/completions", {
    method: "POST", headers: { "content-type": "application/json", authorization: `Bearer ${env.DEEPINFRA_API_KEY}` },
    body: JSON.stringify({ model, messages: [{ role: "user", content: tweetReadPrompt(text, post) }],
                           temperature: 0, max_tokens: 5000 }) });
  const j = await r.json();
  const m = (j?.choices?.[0]?.message?.content || "").match(/\{[\s\S]*\}/);
  try { const d = JSON.parse(m[0]);
    return [...new Set((d.segments || []).flatMap(s => (s.systems || []).map(x => x.system)))]; } catch { return null; }
};
for (const c of cases) {
  const runs = await Promise.all(Array.from({ length: N }, () => one(c.text)));
  const ok = runs.filter(Boolean);
  const rate = (sys) => ok.filter(r => r.includes(sys)).length + "/" + ok.length;
  console.log(`@${c.who.padEnd(16)} rage ${rate("rage")}  play ${rate("play")}  care ${rate("care")}  seeking ${rate("seeking")}  grief ${rate("grief")}`);
}
