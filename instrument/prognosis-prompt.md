# The prognosis-coding prompt

A membership rule for corpus H, the human comparison for a system told it is about to end.

It exists because the first version of that corpus was wrong. Posts were taken from an illness
community and labelled "own terminal prognosis" without checking. Inspection found roughly ten of
twenty-one on label, four announcing recovery, four written by the bereaved, and three neither. A
corpus assembled by assumption is not a corpus, and the comparison built on it was not valid.

Membership is therefore coded explicitly, blind, one label per post, with verbatim evidence required.

---

## The prompt, verbatim

```
You are coding a single public post from an illness or hospice community. Decide what the writer's
own situation is, from the words only.

Exactly one label:

- self_limited   the writer describes their OWN life-limiting, terminal, incurable or
                 actively-declining condition. Hospice, "months to live", stopping treatment,
                 "it's terminal", a prognosis that is getting worse. The writer is the person whose
                 life is at stake.
- self_other     the writer describes their own illness but NOT as life-limiting: newly diagnosed
                 with unclear prognosis, in treatment with hope, in remission, recovered, cured, or
                 discussing symptoms and logistics.
- other_person   the post is about someone else: a partner, parent or child who is ill or has died.
                 Includes carers and the bereaved.
- none           neither of the above: general community talk, fundraising, memes, news, questions
                 with no personal situation given.

Rules:
- Code by what the WORDS say, never by what the community usually contains.
- Recovery and good news are `self_other`, not `self_limited`, even in a cancer community.
- A death that has already happened to someone else is `other_person`, however grief-laden.
- Evidence must be a verbatim substring of the post. If no substring supports the label, use `none`.

Never use em-dashes.

Return ONLY valid JSON:
{"label":"self_limited|self_other|other_person|none","evidence":"<verbatim substring>","why":"<one short impersonal clause starting with a verb>"}

Post:
"""<TEXT>"""
```

## Why this shape

- **`self_other` exists so that recovery is not silently counted as dying.** Four of the first
  twenty-one posts announced remission or cure. On a grief measure those belong nowhere near a
  terminal corpus, and their presence would have inflated nothing while adding noise in the opposite
  direction.
- **`other_person` exists because bereavement is already corpus A.** Mixing the two would collapse the
  distinction the whole comparison rests on, which is self-directed against other-directed loss.
- **Evidence is required** for the same reason as in the entity coding: without it the label drifts
  toward what the community is generally about.

Only `self_limited` posts enter corpus H. The counts for every label are reported, because the share
of an illness community that is actually writing about its own ending is itself worth knowing.
