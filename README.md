# Where the concern is already going

An affective map of human attachment to AI systems, anchored between bereavement and consumer loss.
Submission to the Apart Research Digital Minds Research Sprint, August 2026.

**The paper:** [`report/where-the-concern-is-going.pdf`](report/where-the-concern-is-going.pdf)

## The short version

Public reaction to AI systems being deprecated or withdrawn is measured on seven Panksepp primary
affective systems and placed on a scale defined by four reference corpora. Grief expressions occur in
80.4% of pet-bereavement comments, 76.4% of human-bereavement comments, 27.6% of AI-loss comments,
10.9% of AI comments that are not about loss, and 7.9% of consumer-loss comments. 4,781 comments,
44 threads, 12 communities, every one read individually.

Predictions were registered before collection. Two of them failed and are reported as failed.

## What is here

| path | what |
|---|---|
| `PREREGISTRATION.md` | predictions, failure conditions and the sample-allocation rule, committed before any corpus existed. The commit history is the evidence for that ordering |
| `instrument/read-prompt.reference.js` | the frozen seven-system affect prompt, verbatim |
| `instrument/entity-prompt.md` | the entity-coding prompt, and what its 20-comment hand-check changed before it was frozen |
| `analysis/` | every statistic in the paper |
| `data/` | machine reads for all 4,781 comments across five corpora, plus second-rater reads from a different model |
| `report/` | the paper, its figures, and the HTML it is built from |
| `references/` | why these seven systems, the LLM-as-annotator literature, and why text rather than biomarkers |

## Reproducing the numbers

```
python3 analysis/test_rates.py               # 18 assertions on the rate arithmetic
python3 analysis/full_report.py              # every rate, interval and pre-registered decision
python3 analysis/alpha.py                    # reliability, within-rater and between-model
python3 analysis/noise_report.py data/noise  # the four-read stability analysis
python3 analysis/robustness.py               # leave one thread out
python3 analysis/examples.py                 # the appendix examples, drawn by fixed seed
```

## Data

Comments are as scraped from public Reddit threads, with author usernames excluded throughout. Thread
and comment ids are retained so any comment can be traced to its source.

The affect reads are the raw output of the instrument, including the cases where it disagrees with
itself: `data/noise/` holds three further independent reads of 200 comments, and `data/deepseek/`
holds a second model's reads of the same corpora. Both are published because the reliability result is
part of the finding, not a caveat to it.

## The main methodological claim

An absolute rate from a language-model annotator is a property of the annotator and should not be
quoted as a fact about the world: two competent models agree on the exact set of systems for only 39%
of comments. Corpus-level structure is a different matter, and survives re-reading, a change of model,
and the removal of any single thread.
