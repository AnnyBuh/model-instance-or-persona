# Model, Instance, or Persona?

**Measuring affective signals in public text after an AI is retired.**
Anna Zhu, PhD Researcher, Babeș-Bolyai University, Cluj-Napoca.
Apart Research Digital Minds Research Sprint, August 2026.

📄 **[report/Zhu-2026-Model-Instance-or-Persona.pdf](report/Zhu-2026-Model-Instance-or-Persona.pdf)** is the submission.

---

## What this is

One of the sprint's tracks asks whether the assistant identifies as a model, an instance, or a
persona. This study puts the same question to its users, because when a company retires a deployed
model the people affected write about it in public, and what they name as lost can be counted.

5,579 public texts were read for seven Panksepp primary affective systems under a prompt frozen
before any collection. Threads written after a real deprecation were compared against two reference
corpora fixed in advance: humans whose person has died, and humans told a paid product will end.

**What was found.** 58.5% of post-deprecation comments name nothing that could be a counterpart at
all. Among those that do, a released model version is named about six times as often as the writer's
own instance, which is the case the literature treats as central. The affect is measurable and it is
not bereavement: grief runs at 27.6% against 76.4%, while rage runs at 57.0%, indistinguishable from
the product-discontinuation corpus.

Applying the identical instrument to model-generated text does not work, and the paper quantifies why
rather than asserting it. A change of elicitation frame moves the measured profile by up to 63 points,
and two annotators disagree 2.7 times more on machine-written text than on human text.

Six predictions registered before collection failed. All six are reported as failed in the paper.

---

## Layout

| path | what it holds |
|---|---|
| `report/` | the submission PDF, its HTML source, every figure, and the preview image |
| `PREREGISTRATION.md` | predictions, failure conditions and the allocation rule, committed before any text was collected |
| `PREREGISTRATION-model-arm.md` | the model arm, registered separately before any generation existed |
| `instrument/` | the frozen read prompt, verbatim, plus the entity and prognosis coding prompts |
| `analysis/` | every statistic, figure and validation in the paper |
| `data/` | every machine-generated read, one JSON record per text, plus the discovery and selection sets |

## Reproducing

```sh
python3 analysis/test_rates.py      # the tests, written before the implementation
python3 analysis/full_report.py     # every rate and interval in the paper
python3 analysis/alpha.py           # Krippendorff's alpha, within- and between-annotator
python3 analysis/robustness.py      # leave-one-thread-out, 32 passes
python3 analysis/nrc_validation.py  # agreement with a lexicon containing no model
python3 analysis/figures.py         # the bar charts
python3 analysis/aura_figures.py    # the aura figures defined in Section 2.4
sh      analysis/build_report.sh     # rebuilds the PDF and the preview image
```

Scripts that call an API read `DEEPINFRA_API_KEY` from the environment.

## Two things worth knowing before reading the numbers

**The pre-registration commits are dated.** That is the point of them. Predictions, failure conditions
and the rule for allocating additional sample were fixed before collection began, which is what makes
the results that held worth anything.

**The instrument is applied by a language model and is reported with its error.** Section 3.4 of the
paper gives test-retest, second-annotator, lexicon and leave-one-thread-out figures. Claims are made
from aggregate rates and never from an individual code.

## LLM usage

Language models are the measuring instrument here, not an aid to the writing. Claude Opus 5 was the
primary annotator for all 5,579 reads and wrote the analysis code and the report under the author's
direction. DeepSeek-V3 was the independent second annotator. The author set the research question,
made all selection and ethics decisions, and is responsible for the contents.

## Data and ethics

Every text is a public post or comment. Nothing was collected from a private forum, and no attempt was
made to identify anyone. What is mapped is discourse, not people.
