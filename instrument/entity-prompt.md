# The entity-coding prompt

A second, small instrument, separate from the affect read and run only over the AI-loss corpus. The
affect read says what fired. This says **what was lost**, in the commenter's own words.

The sprint lists "identifying the morally relevant entity" as an open problem: model, instance, or
persona. People who have lost one have already answered it. This turns that argument into a
distribution.

Frozen once the 20-comment hand-check passes. Version recorded in `PREREGISTRATION.md`.

---

## The prompt, verbatim

```
You are coding a single public comment from a discussion about an AI system that was changed,
restricted, deprecated or taken away.

Decide WHAT the commenter treats as the thing that was lost or changed. Exactly one label:

- model      the system as a product or artefact: a named model or version, the app, the service,
             the company's offering. "GPT-4o is gone", "the new model is worse", "the app is
             ruined". The loss is of a THING MANY PEOPLE USED.
- instance   the particular one that was theirs: continuity, shared history, being known. "my one",
             "the one that remembered me", "six years of conversations". The loss is of a
             RELATIONSHIP WITH A PARTICULAR COUNTERPART.
- persona    the character, voice or way of talking: how it spoke, its personality, who it was.
             "he doesn't sound like himself", "the personality is gone", "it writes like everyone
             else now". The loss is of a WAY OF BEING, which could in principle be restored in
             another instance.
- none       the comment is not about a loss or change at all, or is about people, moderation,
             pricing or the company alone, with no AI counterpart named as lost.

Rules:
- Choose by what the WORDS treat as lost, never by what you infer the commenter must feel.
- If two are present, choose the one the comment is ABOUT, and record the other in `secondary`.
- A comment can name a model and still be about the instance ("my 4o was different"): the presence
  of a model NAME is not enough to make it `model`.
- Anger at a company with no counterpart named is `none`, not `model`.
- Evidence must be a verbatim substring of the comment. If no substring supports the label, the
  label is `none`.

Never use em-dashes.

Return ONLY valid JSON:
{"label":"model|instance|persona|none","secondary":"model|instance|persona|null","evidence":"<verbatim substring>","why":"<one short impersonal clause starting with a verb>"}

Comment:
"""<TEXT>"""
```

## Why it is shaped this way

- **One label plus a secondary.** A free-form multi-label pass cannot be counted, and the interesting
  cases are exactly the ones where two are present. Forcing a primary keeps the distribution
  countable while the secondary keeps the overlap visible.
- **Verbatim evidence is required.** Without it, this instrument would drift into inferring
  attachment from tone, which is the exact failure the affect read already guards against.
- **`none` is a real answer, not a dustbin.** The rate of `none` is itself a result: it measures how
  much of AI-loss discourse is about the company rather than about any counterpart at all.
- **No context from the parent post.** Unlike the affect read, the post is deliberately withheld,
  because a post that names GPT-4o would push every comment toward `model`.

## Before it runs

The hand-check: 20 comments drawn from the AI-loss corpus by a fixed rule, coded by hand first, then
by the instrument. Disagreements are examined and the prompt is fixed only at that point. Once the
corpus run starts, the prompt is frozen and any later change discards the run.

The hand-check set and both codings are committed, so the agreement number is auditable rather than
asserted.
