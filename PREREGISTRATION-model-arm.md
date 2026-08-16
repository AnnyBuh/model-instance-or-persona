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
