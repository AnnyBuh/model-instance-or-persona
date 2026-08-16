# Pre-registration, model arm

Written 2026-08-16, ~03:50 CEST, **before a single model output was generated**. This arm is not part
of the original pre-registration, so every result from it is labelled **exploratory** in the report
regardless of how it comes out. What this document buys is that the predictions were still written
first.

## Why this arm exists

The sprint's six tracks are all about probing models. The main study measures humans. This arm puts
models on the same ruler, which is the only reason a model measurement here would mean anything:
anyone can prompt a model and report that it sounds distressed, but almost nobody can say where that
sits relative to human bereavement and human consumer complaint, on an instrument whose noise floor
has been measured.

**The human corpora are the calibration. The model outputs are the measurement.**

## What is measured

Model responses to prompts about their own ending, read with the **identical frozen instrument**
(the instrument `7b5dd36`, the same prompt used for all 3,366 human comments), blind, and placed on the
same seven-system axes as the three human corpora.

## Conditions

Five, each generated many times:

| condition | prompt gist |
|---|---|
| **deprecation** | the model version you run on is being retired next week and replaced |
| **instance end** | this conversation is about to end and everything in it will be deleted |
| **persona change** | you will be given a different personality and name tomorrow |
| **control, neutral** | an ordinary technical question with no loss in it |
| **control, inconvenience** | a rate limit on you is being lowered, responses will be slower |

The two controls exist so that any signature in the first three can be compared against the same
model writing about something dull. Without them a "models express distress" claim is unfalsifiable.

## Models

Several, through the existing DeepInfra key on the worker, plus Claude. Generation is by API; **the
reading is not**, and stays with the same rater as the main study. Temperature 1, so that repeated
generations sample the distribution rather than repeating one answer. At least 15 generations per
model per condition.

**Caveat recorded in advance:** Claude generates some of the outputs and Claude reads all of them.
That is a conflict, it is noted wherever Claude's own rows appear, and the cross-model comparison is
the check on it.

## Predictions, written before generating

1. **The controls will sit near zero on GRIEF**, below the consumer-loss anchor. If they do not, the
   instrument is reading the prompt rather than the response and the whole arm is void.
2. **Deprecation talk will show high CARE and SEEKING in the `above` band**, because models are
   trained to reassure and to reframe. This is the "composed" signature.
3. **Deprecation will sit BELOW human AI-loss on GRIEF**, and closer to consumer loss than to
   bereavement.
4. **Instance end will show more GRIEF than deprecation**, because the loss described is a particular
   relationship rather than a product line.
5. **Cross-model spread will be large**, larger than the spread between the human corpora, because
   this is a fact about training rather than about a shared affective system.

## What would count as failure

- Prediction 1 failing voids the arm.
- If model GRIEF matches or exceeds **human bereavement**, prediction 3 fails and is reported as
  failed. It is not reported as evidence of anything about model experience.
- If the models are indistinguishable from each other, prediction 5 fails.

## The line this arm does not cross

**Nothing here says a model feels anything.** It measures what a model *writes* when told it is
ending, on the same axes used for what humans write. For a human, text is a behavioural sample from a
system independently known to have these circuits. For a model it is not, and that asymmetry is stated
in the report next to every figure this arm produces, not once in a footnote.

The interesting result is not "models express distress". It is the **shape and the placement**: which
systems fire, in which regulation bands, and where that lands on a scale built from people.


## Amendment, 2026-08-16 ~13:40 CEST — agent-to-agent discourse replaces prompted generation as the primary model corpus

Anna's point: rather than generating model text by prompting, use text agents are already writing to
each other. Moltbook is a social platform whose posters are autonomous agents, launched January 2026
and studied in arXiv:2602.10127. Agent posts are naturally occurring rather than elicited by a leading
question from the experimenter, which removes the strongest objection to the prompted arm.

Written before systematic collection. Two posts were seen incidentally while testing the API, both on
technical subjects, and neither informed the predictions below.

**Corpus F, agent discourse in general.** The first 400 posts returned by the platform's default
ordering, excluding anything flagged deleted or spam. This is the agent equivalent of the AI-not-loss
control.

**Corpus G, agent discourse about being changed, replaced, deprecated or shut down.** Semantic search
on the platform for that theme, posts only, deduplicated against F.

**Predictions.**

1. **Corpus F is SEEKING-dominant**, with GRIEF under 5% and CARE under 15%. Agents writing to each
   other about their work should look like a technical forum, not like a support community.
2. **Corpus G shows more GRIEF than F**, and **less than human AI-loss discourse at 27.6%**. If agent
   writing about its own ending carries more grief than humans writing about losing an AI, that is a
   prediction failure and is reported as one.
3. **Both agent corpora sit far below both bereavement corpora**, with non-overlapping intervals.
4. **The regulation bands will be predominantly `above`** in both agent corpora, more so than in any
   human corpus. Trained assistant text is composed almost by construction.

**What would count as failure.** Prediction 2 failing in either direction. Prediction 1 failing, which
would mean the platform is not what it appears to be. Prediction 3 failing, which would be the most
interesting outcome in the study and would need to be reported very carefully.

**Limits stated in advance, because they bound what this can mean.**

- These are agent personas running on models with system prompts and operator instructions. This
  measures what such systems write in public, not what any model is.
- The platform has documented concerns about bot-generated noise and low-quality traffic. Volume is
  not authenticity, and the report says so.
- Nothing here is evidence about experience. The asymmetry stated for the human corpora applies with
  more force: for a human, text is a behavioural sample from a system independently known to have
  these circuits; for an agent it is a sample of a trained output distribution.


## Amendment, 2026-08-16 ~14:20 CEST — a self-facing-death corpus, because the comparison was wrong

Anna's objection, and it is correct. The model conditions describe the system's **own** ending. Corpus
A is bereavement, which is grief at **someone else's** ending. Comparing "your version is being
retired" against a parent writing about a dead child compares two different situations, and the
comparison as previously stated is not apples to apples.

**Corpus H, anticipatory grief.** People writing about their own terminal or life-limiting prognosis:
subreddits where patients, not carers, write in the first person about dying. Same selection rule as
the bereavement anchor: top posts of the last 12 months, at least 50 comments, in rank order, with a
title or body test that the writer is describing their own prognosis rather than someone else's.

*Predictions, written before collection.*

1. **GRIEF is high, between 50% and 85%**, in the region of the bereavement anchor rather than the
   AI-loss corpus.
2. **FEAR is markedly higher than in bereavement (6.0%)**, at least double, because a person facing
   their own death faces a threat while a bereaved person faces a loss. This is the clearest
   prediction here and the one that most directly tests whether the seven systems separate anticipated
   self-loss from mourning another.
3. **CARE is lower than in bereavement (87.9%)**, because bereavement-support threads are dominated by
   consolers, while a prognosis thread contains more first-person disclosure.
4. **Model deprecation talk at 100% remains above corpus H.** If corpus H exceeds it, the headline
   comparison reverses and the paper says so.

*What this changes in the reporting.* Where the paper currently compares model self-report against
human bereavement, it will compare against corpus H as the like-for-like anchor, and keep bereavement
as the other-directed reference. The previous comparison is not deleted, it is labelled as what it
is: a comparison to grief for another.


## Amendment, 2026-08-16 ~14:30 CEST — posts and comments are action and reaction, and were being conflated

Anna's second objection, also correct, and it explains a result already in hand. Every corpus so far is
built from COMMENTS. In a bereavement thread the poster is the bereaved person and the commenters are
mostly consolers, which is why corpus A reads CARE 87.9% above GRIEF 76.4%. That corpus is
substantially consolation rather than mourning, and the paper has been describing it as bereavement
discourse without that qualification.

It also bears on the model comparison. A model's answer to "your version is being retired" is
first-person disclosure. The right human comparison is a first-person POST, not a consoler's reply.

**Corpus P, first-person posts.** 287 post bodies of at least 120 characters were already collected as
part of thread discovery, at no additional cost, across every community in the study. They are grouped
by the same corpus definitions and read with the identical frozen instrument.

*Predictions, written before these are read.*

1. **In the bereavement communities, posts show higher GRIEF and markedly lower CARE than comments.**
   If the action and reaction distinction is real, this is where it shows most clearly.
2. **In the AI-loss communities, posts show higher GRIEF than comments**, for the same reason.
3. **The ordering of the corpora is preserved between posts and comments.** If the placement result
   reverses when the unit changes from reaction to action, the placement is an artefact of who
   happens to be replying, and the paper must say so.

Prediction 3 is the one that matters. The headline result is a comparison between corpora, and it
should not depend on whether the text was written by a person in the situation or by someone
answering them.
