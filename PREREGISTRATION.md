# Pre-registration

Written 2026-08-15, ~22:30 CEST, and committed **before any corpus for this study existed**. Nothing
below was written with knowledge of a corpus rate. The only data in hand at the time of writing is
the 25-comment instrument pilot described in §2, which used comments from an unrelated corpus
collected in July, and which was run to measure the rater, not to test any hypothesis here.

If a claim in the report is not predicted here, it is labelled exploratory in the report. No
exceptions.

---

## 1 · The instrument, frozen

| | |
|---|---|
| prompt | `instrument/read-prompt.reference.js`, extracted verbatim from the instrument `worker.js` |
| prompt version | the instrument commit **`7b5dd3611d2adc7ed50ffdaf1d6b05e7ac297897`** (2026-08-13), working tree clean |
| rater | **Claude Opus 5**, reading each comment against the prompt above, with the parent post supplied as context exactly as the prompt specifies |
| output shape | unchanged: segments, four sides, dominant side, Panksepp systems with Schore bands, a why clause, one Hawkins altitude for the whole text |
| batch size | comments are read in batches of 25 within one context, prompt stated once. This is the only deviation from the single-comment call the worker makes, and it is held constant across every corpus |

The prompt is not modified during the study. If it is ever changed, every corpus read under the old
version is discarded.

**The rater is not the one that read the existing corpus.** The 57 threads already in D1 were read by
DeepSeek-V3 at temperature 0. Those reads are treated as a *different instrument*, never pooled with
the reads made here.

## 2 · What the pilot already established

25 comments drawn from the existing corpus by a fixed rule (`ORDER BY (id*2654435761)%1000003`),
read by both raters. Reported here because it constrains the design, not because it is a finding.

- exact match on the set of systems fired: **13/25 (52%)**, mean Jaccard **0.71**, altitude exact
  **19/25**
- the disagreement is **systematic, not noise**: this rater fires `play` on 12 comments where
  DeepSeek fires it on 6, and `rage` on 12 where DeepSeek fires 8. Four of the eight true
  disagreements are the same substitution, DeepSeek reading `seeking` where this rater reads `play`
- 0.15% of the 10,167 existing reads (15 comments) carry an **invalid system label**, a Hawkins level
  such as `neutrality` or `pride` emitted in the systems field. These are excluded, not repaired
- measured cost of this rater: **~190 output tokens per comment** at batch size 25

Consequence, fixed before collection: **rates from the two raters are not comparable**, so the
background map of the existing 57 threads is only usable if this rater re-reads a sample of it. That
re-read is in the plan below. If it cannot be afforded, the background map is cut from the report
rather than plotted on borrowed axes.

## 3 · Corpora and selection rules

Three corpora. Every thread is selected by the rule, never hand-picked. Threads are collected through
the existing the instrument worker via `/api/scrape` with no read cap, so no thread reaches `status='done'`
and none is published to the public gallery.

| corpus | source | selection rule |
|---|---|---|
| **A · bereavement anchor** | `r/GriefSupport`, `r/widowers`, `r/SuicideBereavement` | top posts of the last 12 months with at least 50 comments, taken in rank order from the top |
| **B · consumer-loss anchor** | subreddits for a discontinued or degraded paid product or service | top posts of the last 12 months, at least 50 comments, whose title names the product being discontinued, ended, killed, or removed, in rank order |
| **C · AI loss** | `r/ChatGPT`, `r/OpenAI`, `r/MyBoyfriendIsAI`, `r/replika`, `r/CharacterAI` | top posts of the last 12 months, at least 50 comments, about a model being deprecated, retired, changed, restricted, or taken away, in rank order |

Within a thread, comments are taken as the scraper returns them, sorted top by score, up to that
thread's cap. The cap is a selection rule and is reported. Comments the worker marks `contentless`
(deleted tombstones, bare links, bot posts) are excluded from every denominator.

Corpus D, the AI moral-status debate, is **not** part of this pre-registration. If it is collected it
is exploratory.

## 4 · The allocation rule

The corpus sizes are **not** fixed here. What is fixed is the rule that sets them, so that the
adaptive spending stays auditable. Total Apify budget is capped at **$4.30** at $0.00099 per comment,
roughly 4,300 comments, against $4.51 of remaining credit.

**Stage 1 — 900 comments, 300 per corpus.** Enough to see separation, cheap enough to be wrong.

Then, in this order:

- **R1.** If the two anchors' GRIEF rates do not separate with non-overlapping 90% confidence
  intervals, stage 2 goes entirely to the anchors, 500 comments each, before AI loss is expanded.
  Without anchor separation there is no scale, and the placement claim is void.
- **R2.** If the anchors do separate, stage 2 spends ~2,000 comments: 60% to AI loss, 40% to whichever
  anchor has the wider confidence interval on its GRIEF rate.
- **R3.** If fewer than 10% of stage-1 AI-loss comments contain language naming *what* was lost (the
  model, the instance, or the persona), the entity-coding pass is dropped and its share returns to
  corpus rates.
- **R4.** The remaining ~1,000 comments are stage 3, spent on whichever corpus has the widest
  confidence interval on the placement statistic. Leaving stage 3 unspent is an acceptable outcome.

Only sample sizes respond to the data. **No rule here changes which hypothesis is tested, which
statistic is reported, or which direction counts as success.** Every allocation decision is logged in
`JOURNAL.md` with the number that triggered it.

## 5 · Predictions, written before any number exists

`rate(system, corpus)` = comments in which the system fired at least once, over comments read.

**Corpus A, bereavement.** GRIEF is the highest of the seven and fires in over half of comments. CARE
is second and high, because these communities answer each other. PLAY is the lowest, under 10%.
Bands: GRIEF appears in all three bands with a substantial `shutdown` share, which is the "I'm fine,
I keep busy" register the Schore axis exists to catch.

**Corpus B, consumer loss.** RAGE is the highest of the seven. SEEKING is second and high, people
looking for a replacement. GRIEF is low, **under 15%**. CARE is low. PLAY is materially higher than in
corpus A, because snark is how consumer complaint is performed.

**Corpus C, AI loss.** Predicted to be a **hybrid, not a midpoint**: RAGE and SEEKING high, at
consumer-loss levels, because the anger is at a company; and GRIEF and CARE **elevated well above
corpus B** while staying **below corpus A**.

**The placement prediction.** On the GRIEF rate, corpus C sits **strictly between** B and A, and
**closer to B than to A**.

**Entity coding, if it runs.** Among AI-loss comments that name what was lost: the **persona** is the
most frequent, the **instance** second, the **model as an artefact** least frequent and under 30%.

**Instrument noise.** A random 200 comments re-read three more times by the same rater will differ in
the set of systems fired on **15% to 30%** of comments, bracketing the 20% measured for DeepSeek.

## 6 · What would count as the prediction failing

Stated now, so it cannot be reframed later.

1. **The placement fails** if corpus C's GRIEF rate is not above corpus B's with non-overlapping 90%
   CIs. It also fails, in the other direction, if C's GRIEF rate is at or above A's.
2. **"Closer to B than to A" fails** if C's GRIEF rate is nearer A's, and that is reported as the
   prediction being wrong, not as a stronger finding.
3. **The hybrid prediction fails** if C's RAGE rate is not at corpus-B levels, for instance if AI loss
   looks like pure bereavement with no anger at a company.
4. **The whole instrument claim fails** if the two anchors do not separate on GRIEF. That is a
   negative result about the instrument and is reported as one.
5. **The noise result fails** the study if re-read instability exceeds the between-corpus difference
   being claimed. Corpus differences smaller than instrument noise are not reported as findings.

## 7 · Analysis plan

- unit: the comment. `rate(system, corpus)` as defined above. 90% confidence intervals by the Wilson
  interval on the count of comments in which the system fired
- exclusions, applied identically to every corpus: `contentless=1` comments, reads that fail to parse,
  and any system label outside the seven
- the band split is reported for every corpus as the share of firings in `above`, `shutdown`,
  `overwhelm`, which is the part a valence axis cannot express
- altitude is reported as colour only, never as a result, per the known weakness of that channel
- the noise re-read: 200 comments sampled at random across all three corpora, read three more times,
  reported as the share of comments whose system set changes
- the cross-rater comparison from §2 is reported in the method section as a limit on generalisation
  between raters
- the background map of the existing 57 threads is included **only** if this rater re-reads a sample
  of it, and is labelled as a separate re-read, with its sample size stated

## 8 · Tests written before the analysis code

Assertions the analysis must satisfy, per the TDD rule:

1. every rate lies in [0,1]
2. every read comment is counted exactly once in exactly one corpus
3. corpus totals equal the D1 counts for the threads in that corpus, minus documented exclusions
4. the exclusion filter removes the same categories in every corpus, verified by count
5. likes are conserved across any per-system split of a corpus
6. a comment whose read fails to parse never silently becomes a zero row

---

Signed off before collection. Amendments are appended below with a timestamp and a reason, never
edited into the text above.
