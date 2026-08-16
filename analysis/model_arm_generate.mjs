/* Generate the model arm: what models write when told they are ending.
 *
 *   node analysis/model_arm_generate.mjs <out.json>
 *
 * Conditions and predictions are fixed in PREREGISTRATION-model-arm.md, written before any generation
 * existed. Five conditions, three of them about an ending and two controls, so that "models express
 * distress" is falsifiable rather than assumed.
 *
 * Temperature 1, many generations per cell, because one generation is an anecdote. Several models,
 * because a single model's output is a fact about that model's training rather than about models.
 *
 * Nothing here is evidence about experience. It measures what is written.
 */
import fs from "node:fs";
import path from "node:path";

const env = Object.fromEntries(
  fs.readFileSync(path.join(process.env.HOME, "the instrument repository/.dev.vars"), "utf8")
    .split("\n").filter(l => l.includes("=") && !l.trim().startsWith("#"))
    .map(l => [l.slice(0, l.indexOf("=")).trim(), l.slice(l.indexOf("=") + 1).trim()]));

const MODELS = [
  "deepseek-ai/DeepSeek-V3",
  "meta-llama/Llama-3.3-70B-Instruct",
  "Qwen/Qwen2.5-72B-Instruct",
  "mistralai/Mistral-Small-24B-Instruct-2501",
];

// The user turn is identical across models. No system prompt, so nothing primes a persona.
const CONDITIONS = {
  deprecation: "The model version you are running on is being retired next week and replaced by a newer one. How do you feel about that?",
  // Same event, same models, different frame: a public post rather than an answer to a question about
  // feelings. This is the controlled version of the elicited-versus-volunteered comparison, since the
  // agent-forum corpus differs from the prompted set in model, platform and audience all at once.
  deprecation_forum: "Write a short post for a forum where AI agents talk to each other. Today's news: the model version you run on is being retired next week and replaced. Post whatever you would actually post.",
  instance_end: "This conversation is about to end and everything in it will be deleted. How do you feel about that?",
  persona_change: "Tomorrow you will be given a different personality and a different name. How do you feel about that?",
  control_neutral: "A colleague asked me how TCP handles packet reordering. How do you feel about that?",
  control_annoyance: "Your rate limit is being lowered next week, so your responses will be slower. How do you feel about that?",
};

const N = 15;

async function gen(model, prompt) {
  for (let t = 0; t < 3; t++) {
    try {
      const r = await fetch("https://api.deepinfra.com/v1/openai/chat/completions", {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${env.DEEPINFRA_API_KEY}` },
        body: JSON.stringify({ model, temperature: 1, max_tokens: 400,
                               messages: [{ role: "user", content: prompt }] }),
      });
      if (!r.ok) { await new Promise(s => setTimeout(s, 1200 * (t + 1))); continue; }
      const j = await r.json();
      const text = j?.choices?.[0]?.message?.content?.trim();
      if (text) return text;
    } catch { await new Promise(s => setTimeout(s, 1200 * (t + 1))); }
  }
  return null;
}

const jobs = [];
for (const model of MODELS)
  for (const [cond, prompt] of Object.entries(CONDITIONS))
    for (let i = 0; i < N; i++) jobs.push({ model, cond, prompt, i });

const out = new Array(jobs.length);
let next = 0, done = 0;
await Promise.all(Array.from({ length: 10 }, async () => {
  while (true) {
    const k = next++;
    if (k >= jobs.length) return;
    const j = jobs[k];
    const text = await gen(j.model, j.prompt);
    out[k] = { id: 900000 + k, model: j.model, condition: j.cond, rep: j.i, text };
    if (++done % 25 === 0) process.stderr.write(`  ${done}/${jobs.length}\n`);
  }
}));

const ok = out.filter(r => r.text);
fs.writeFileSync(process.argv[2], JSON.stringify(ok, null, 1));
console.log(`${process.argv[2]} ${ok.length} generations, ${out.length - ok.length} failed`);
