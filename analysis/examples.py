"""Draw illustrative examples for the paper by rule, not by taste.

    python3 analysis/examples.py

Quoting examples is how a reader understands what is being coded. It is also the easiest place in a
study like this to lose credibility, because a reader cannot distinguish an illustration from a
cherry-pick. Three rules, all enforced here rather than promised in prose:

1. **Selection is by fixed rule with a disclosed seed.** Every example below is reproducible by running
   this file. Nothing was chosen because it read well.
2. **Examples illustrate the coding scheme. They are never evidence for a rate.** The instrument
   disagrees with itself on a third of comments, so no single comment supports anything.
3. **The awkward cases are drawn too**, on the same terms: comments where the four re-reads disagreed,
   and comments where the two models disagreed. Showing only clean cases would misrepresent the
   instrument.

Quotes are truncated to 220 characters and are not attributed to usernames, though the underlying
data retains them, because attribution adds nothing to a rate and takes something from the person.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260816
STAGES = ("stage1", "stage2", "stage3", "stage4")
NAMES = {"A": "human bereavement", "B": "consumer loss", "C": "AI loss",
         "D": "AI, not loss", "E": "pet loss"}
LIMIT = 220


def load():
    text, cmap, reads = {}, {}, {}
    for stage in STAGES:
        d = os.path.join(ROOT, "data", stage)
        for c in json.load(open(os.path.join(d, "%s-comments.json" % stage))):
            text[c["id"]] = c["text"]
        cmap.update({int(k): v for k, v in json.load(open(os.path.join(d, "corpus-map.json"))).items()})
        for name in sorted(os.listdir(os.path.join(d, "reads"))):
            if name.endswith(".reads.json"):
                for r in json.load(open(os.path.join(d, "reads", name))):
                    reads[r["id"]] = r
    return text, cmap, reads


def clean(s):
    return " ".join(s.split())[:LIMIT]


def main():
    text, cmap, reads = load()
    rng = random.Random(SEED)

    print("A. One comment drawn at random from each corpus, seed %d, no other condition.\n" % SEED)
    for c in ("E", "A", "C", "D", "B"):
        ids = sorted(i for i in reads if cmap.get(i) == c and len(text.get(i, "")) > 60)
        cid = rng.choice(ids)
        r = reads[cid]
        bands = sorted({"%s/%s" % (f["system"], f["band"])
                        for s in r["segments"] for f in s["systems"]})
        why = next((s.get("why") for s in r["segments"] if s.get("why")), "")
        print("  %-18s %s" % (NAMES[c], ", ".join(bands) or "no system fired"))
        print("     \"%s\"" % clean(text[cid]))
        print("     read: %s\n" % why)

    print("\nB. Comments where the four independent reads did NOT agree, drawn at random from that set.\n")
    ids = set(json.load(open(os.path.join(ROOT, "data/noise-sample-ids.json"))))
    rounds = {}
    nd = os.path.join(ROOT, "data", "noise")
    for name in sorted(os.listdir(nd)):
        if name.endswith(".reads.json"):
            k = int(name[5])
            rounds.setdefault(k, {})
            for r in json.load(open(os.path.join(nd, name))):
                rounds[k][r["id"]] = r
    unstable = []
    for i in sorted(ids):
        if i in reads and all(i in rounds[k] for k in rounds):
            sets = [frozenset(rates.systems_fired(reads[i]))] + \
                   [frozenset(rates.systems_fired(rounds[k][i])) for k in sorted(rounds)]
            if len(set(sets)) > 1:
                unstable.append((i, sets))
    rng2 = random.Random(SEED + 1)
    for i, sets in rng2.sample(unstable, min(3, len(unstable))):
        print("  %-18s" % NAMES[cmap[i]])
        print("     \"%s\"" % clean(text[i]))
        print("     four reads: %s\n" % " | ".join(", ".join(sorted(s)) or "none" for s in sets))

    print("\nC. Comments where the two models disagreed, drawn at random from that set.\n")
    ds = {}
    dd = os.path.join(ROOT, "data", "deepseek")
    for name in sorted(os.listdir(dd)):
        if name.endswith(".json"):
            for r in json.load(open(os.path.join(dd, name))):
                if not r.get("failed"):
                    ds[r["id"]] = r
    disagree = [i for i in sorted(ds)
                if i in reads and len(text.get(i, "")) > 60
                and rates.systems_fired(reads[i]) != rates.systems_fired(ds[i])]
    rng3 = random.Random(SEED + 2)
    for i in rng3.sample(disagree, min(3, len(disagree))):
        print("  %-18s" % NAMES[cmap[i]])
        print("     \"%s\"" % clean(text[i]))
        print("     Claude: %s" % (", ".join(sorted(rates.systems_fired(reads[i]))) or "none"))
        print("     DeepSeek: %s\n" % (", ".join(sorted(rates.systems_fired(ds[i]))) or "none"))


if __name__ == "__main__":
    main()
