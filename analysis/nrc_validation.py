"""External validation: does a human-built lexicon rank the corpora the way our instrument does?

    python3 analysis/nrc_validation.py <path to NRC-Emotion-Lexicon-Wordlevel.txt>

Every reliability check in this study so far is internal. Re-reading measures the annotator against
itself, and a second model measures one annotator against another. Neither tells us the instrument
tracks anything outside language models.

The NRC Emotion Lexicon is a word-emotion association list built by human crowd annotation, with no
model anywhere in it. It is a crude instrument: it counts words, ignores negation, irony and context,
which is exactly what the affective read exists to handle. That crudeness is the point. If a
word-counting list built by people independently produces the same ORDERING of corpora as the
seven-system read, the read is tracking something real in the text rather than something internal to
the annotator. If it does not, that has to be reported.

Two comparisons:

1. **Corpus level.** Mean NRC sadness density per corpus, against our GRIEF rate.
2. **Thread level.** Spearman rank correlation across all threads between NRC sadness density and our
   GRIEF rate. This is the stricter test: it asks whether the two instruments agree on the ordering of
   44 individual threads, not just on five well-separated groups.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGES = ("stage1", "stage2", "stage3", "stage4")
NAMES = {"A": "human bereavement", "B": "consumer loss", "C": "AI loss",
         "D": "AI, not loss", "E": "pet loss"}
TOKEN = re.compile(r"[a-z']+")


def load_lexicon(path, emotions=("sadness", "joy", "anger", "fear")):
    lex = {e: set() for e in emotions}
    for line in open(path, encoding="utf8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        word, emotion, flag = parts
        if emotion in lex and flag == "1":
            lex[emotion].add(word)
    return lex


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):          # average ranks within ties
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def main(lex_path):
    lex = load_lexicon(lex_path)
    print("NRC lexicon: %s" % {e: len(w) for e, w in lex.items()})

    comments, cmap, thread = {}, {}, {}
    for stage in STAGES:
        d = os.path.join(ROOT, "data", stage)
        for c in json.load(open(os.path.join(d, "%s-comments.json" % stage))):
            comments[c["id"]] = c["text"]
            thread[c["id"]] = c["thread"]
        cmap.update({int(k): v for k, v in json.load(open(os.path.join(d, "corpus-map.json"))).items()})

    reads = []
    for stage in STAGES:
        rd = os.path.join(ROOT, "data", stage, "reads")
        for name in sorted(os.listdir(rd)):
            if name.endswith(".reads.json"):
                reads.extend(json.load(open(os.path.join(rd, name))))

    # NRC density per comment: share of tokens carrying the emotion
    dens = {}
    for cid, text in comments.items():
        toks = TOKEN.findall(text.lower())
        if not toks:
            continue
        dens[cid] = {e: sum(1 for w in toks if w in lex[e]) / len(toks) for e in lex}

    R = rates.corpus_rates(reads, cmap)

    print("\n1. Corpus level")
    print("   %-20s %-12s %-14s %-12s" % ("corpus", "our GRIEF", "NRC sadness", "NRC joy"))
    rows = []
    for c in ("E", "A", "C", "D", "B"):
        ids = [i for i in dens if cmap.get(i) == c]
        sad = 1000 * sum(dens[i]["sadness"] for i in ids) / len(ids)
        joy = 1000 * sum(dens[i]["joy"] for i in ids) / len(ids)
        g = 100 * R[c]["rates"]["grief"]["rate"]
        rows.append((c, g, sad))
        print("   %-20s %-12.1f %-14.1f %-12.1f" % (NAMES[c], g, sad, joy))
    print("   NRC values are sadness words per 1,000 tokens.")
    print("   corpus-level rank agreement: %s"
          % ("SAME ORDERING" if [r[0] for r in sorted(rows, key=lambda r: -r[1])]
             == [r[0] for r in sorted(rows, key=lambda r: -r[2])] else "DIFFERENT ORDERING"))

    print("\n2. Thread level, the stricter test")
    per_thread = {}
    for r in reads:
        t = thread[r["id"]]
        per_thread.setdefault(t, {"n": 0, "grief": 0, "sad": 0.0, "sn": 0})
        per_thread[t]["n"] += 1
        if "grief" in rates.systems_fired(r):
            per_thread[t]["grief"] += 1
        if r["id"] in dens:
            per_thread[t]["sad"] += dens[r["id"]]["sadness"]
            per_thread[t]["sn"] += 1
    xs, ys = [], []
    for t, v in sorted(per_thread.items()):
        if v["n"] >= 30 and v["sn"]:
            xs.append(v["grief"] / v["n"])
            ys.append(v["sad"] / v["sn"])
    rho = spearman(xs, ys)
    print("   threads compared: %d" % len(xs))
    print("   Spearman rho between our GRIEF rate and NRC sadness density: %.3f" % rho)
    json.dump({"corpus": [{"corpus": c, "grief": g, "nrc_sadness_per_1k": s} for c, g, s in rows],
               "thread_spearman": rho, "n_threads": len(xs)},
              open(os.path.join(ROOT, "data", "nrc-validation.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
