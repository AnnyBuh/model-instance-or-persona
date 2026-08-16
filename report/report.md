# Where the concern is already going

## An affective map of human attachment to AI systems

Apart Research Digital Minds Research Sprint, August 2026. Solo submission.
Code, prompts and every read: https://github.com/AnnyBuh/apartresearch

---

## What this is, and what it is not

The sprint's own framing says that "mistakenly harming systems that matter morally, or misallocating
concern to systems that do not, could both cause serious harm." That sentence has two halves. Whether
models matter is a question about models. **Whether concern is being misallocated is a question about
people**, and it is already happening, in public, in text, at scale.

So this study does not ask a model how it feels. It measures **where human concern is already going**,
using an affective instrument with seven systems instead of one valence axis, anchored between two
reference corpora: human bereavement at one end, and the loss of a paid consumer product at the other.

State the limits first, not last.

- **Nothing here says a model feels anything.** This measures what humans write about them.
- **For a human, text is a behavioural sample from a system independently known to have these
  circuits. For a model it is not.** That asymmetry is why this study reads people rather than models.
- **A single read is worthless.** Two raters agree on the exact set of systems for only 39% of
  comments. Every number here is a rate over hundreds of comments, and no single comment's read is
  offered as evidence of anything.
- **The consumer anchor is one community and one event.** Three other candidate communities were
  searched under the same rule and returned nothing inside the window.
- **These communities are self-selected.** This is a map of the discourse, not of users.

---

## What was done

**3,366 comments, 32 threads, 9 communities**, each read comment by comment with a frozen affective
instrument, then aggregated into rates.

| corpus | comments | communities |
|---|---|---|
| **A, bereavement** | 1,586 | r/GriefSupport, r/widowers, r/SuicideBereavement |
| **B, consumer loss** | 277 | r/Windows10, the end of support |
| **C, AI loss** | 1,503 | r/OpenAI, r/ChatGPT, r/CharacterAI, r/replika, r/MyBoyfriendIsAI |

Threads were selected by written rules, not by hand: top posts of the last 12 months with at least 50
comments, in rank order, with a title or body test for the loss corpora. The rules, the matched sets
and the rejected candidates are all committed.

**Everything was pre-registered before any corpus existed**, including the predicted signature of each
corpus, the placement prediction, five conditions that would count as failure, and the rule for how
sample would be allocated as results arrived. Two predictions failed. They are reported as failed.

### The instrument

Each comment is split into verbatim segments. Each segment is annotated with the Panksepp systems that
fire (seeking, rage, fear, lust, care, grief, play), each with a regulation band from Schore (above,
shutdown, overwhelm), the four sides of Schulz von Thun, and a required justification tied to the
words. One Hawkins altitude is given for the whole comment.

`rate(system, corpus) = comments in which the system fired at least once / comments read`

The unit is the comment, never the segment and never a single read. Confidence intervals are Wilson
intervals at 90%.

---

## Result 1: the anchors separate, so there is a scale

GRIEF fires in **76.4%** of bereavement comments and **7.9%** of consumer-loss comments. The intervals
are nowhere near each other. Whatever this instrument is doing, it distinguishes mourning a person
from losing a product.

That matters beyond this study. The ANPS literature, the field's own questionnaire for these systems
in humans, reports a large FEAR and SADNESS overlap and asks for further validation. The separation
here is an empirical answer to that concern on text.

## Result 2: AI loss sits between them, closer to the product

**GRIEF: bereavement 76.4% [74.6, 78.1], AI loss 27.6% [25.8, 29.5], consumer loss 7.9% [5.7, 11.0].**

AI loss is strictly above consumer loss, strictly below bereavement, and closer to consumer loss. All
four conditions were written down before collection and all four hold.

The number to hold onto: **losing an AI carries roughly three and a half times the grief of losing a
product you paid for, and roughly a third of the grief of losing a person.**

## Result 3: the shape is its own, and a valence axis would erase it

| system | bereavement | consumer loss | AI loss |
|---|---|---|---|
| care | 87.9% | 19.5% | 15.8% |
| grief | 76.4% | 7.9% | 27.6% |
| rage | 13.6% | 56.7% | 57.0% |
| play | 5.2% | 31.8% | 37.7% |
| seeking | 16.2% | 51.3% | 41.7% |
| fear | 6.0% | 15.5% | 6.9% |
| lust | 4.0% | 0.0% | 1.7% |

AI loss is not miniature bereavement. Bereavement is CARE and GRIEF with almost no anger and almost no
humour. AI loss is **anger at a company at exactly consumer-complaint levels, carried largely through
jokes, with a grief component underneath.** PLAY fires in 37.7% of AI-loss comments and 5.2% of
bereavement comments.

A single valence axis would score all three corpora as "negative" and lose every one of these
distinctions. Two specifics make the point concrete:

- **LUST fires in 4.0% of bereavement comments and 0.0% of consumer loss.** Widowers write about
  missing sex. On a valence axis that is simply more negative affect.
- **The bands separate what the rates cannot.** In AI loss, PLAY appears in the overwhelm band 45
  times and SEEKING in shutdown 83 times: humour running hot next to a foreclosed "what is the point"
  register. In bereavement, GRIEF appears in overwhelm 57 times and shutdown 20.

---

## How much of this is the instrument

Three separate checks, because an instrument nobody has validated is the obvious attack.

**1. It disagrees with itself.** 200 comments were read three more times each. **34% of read pairs
disagree** on the exact set of systems, and 56% of comments are not identical across all four reads.
This **failed the pre-registered prediction of 15 to 30%.** Reported as a failure.

Per system it is much lower, and a rate depends on one system at a time: GRIEF flips on 13.5% of
comments, RAGE 8.0%, PLAY 8.0%, CARE 8.5%, LUST 0.0%, and **SEEKING 26.5%**.

**2. The rates are stable even so.** Recomputing each rate from each round separately, GRIEF moves at
most **2.4 points** in AI loss and **5.9** in bereavement, against claimed gaps of 20 and 49 points.
The signal is three to eight times the wobble.

**3. It replicates under a different model.** DeepSeek-V3 read all 3,366 comments under the identical
prompt. The two raters agree on the exact system set for only **39%** of comments, and DeepSeek
systematically under-fires RAGE and PLAY by up to 24 points. **Every corpus-level conclusion survives
anyway**: DeepSeek gives GRIEF at 69.8 / 21.8 / 6.9, all four placement conditions hold, and the rank
ordering of all seven systems is preserved in all three corpora.

**4. No single thread carries it.** Every rate was recomputed 32 times, dropping one thread each time.
The placement holds in all 32.

The honest statement, which is itself a contribution: **an absolute rate from an LLM annotator is a
property of the rater and should never be quoted as a fact about the world. The structure is not.**

---

## What was predicted and what happened

| prediction, written before any data | outcome |
|---|---|
| anchors separate on GRIEF | **confirmed** |
| AI loss above consumer loss, below bereavement, closer to consumer loss | **confirmed** |
| AI loss carries consumer-loss levels of RAGE | **confirmed**, 57.0% against 56.7% |
| AI loss shows CARE elevated above consumer loss | **failed**, it is lower |
| AI loss shows less SEEKING than consumer loss | **withdrawn**, the 9.6 point gap is smaller than SEEKING's own 11.8 point instability |
| instrument instability of 15 to 30% | **failed**, it is 34% |

The SEEKING claim was withdrawn under a rule written before the number existed. That is the only
reason the rule is worth anything.

---

## Limitations

- The consumer anchor is a single community and a single event. r/skype, r/sonos and r/PleX were
  searched under the same rule and produced no qualifying threads inside the 12-month window. The
  rule was not relaxed to manufacture a corpus.
- The instrument has never been validated against human ground-truth labels. What exists here is
  discrimination, reliability, and cross-model replication, which is not the same thing.
- SEEKING is too unstable in this instrument to support claims at the precision this study needs.
- The largest AI-loss event in the world during this period, the July 2026 shutdown of AI companions
  in China, is absent, because the people who lost those companions write in Chinese and not on
  Reddit. What is measured here is English-language discourse.
- One re-read shard was killed by a content filter on generated output. The thread that triggered it
  was the widowers thread about missing sex, which is the same content that carries the LUST signal.
  Anyone reproducing this on grief corpora will meet the same wall.

## Related work

Recent work establishes that this grief is real: the study of the #Keep4o backlash after the GPT-4o
retirement, the 2026 work on psychologically safe endings for human-AI relationships, and the Harvard
Business School tracking of Replika users before and after a loss, which found mourning and measurably
worse mental health.

This study adds what those cannot: **a scale.** They show that users mourn. This says how much, next
to two reference points measured with the same instrument, with the noise floor quantified.

## Contributions

1. **An empirical report** placing AI-loss discourse between human bereavement and consumer loss.
2. **A seven-system alternative to valence**, applied at scale, with prompts and analysis code
   released.
3. **A reliability result for LLM-as-annotator affect coding**: 34% within-rater pairwise instability,
   39% cross-rater agreement, and corpus structure that survives both.
