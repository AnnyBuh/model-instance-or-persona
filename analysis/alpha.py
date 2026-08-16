"""Krippendorff's alpha for the two reliability questions this study has to answer.

    python3 analysis/alpha.py

Percent agreement is not a reliability statistic: two coders who both say "no" 90% of the time agree
90% of the time by construction. Alpha corrects for chance agreement and is the coefficient the
LLM-as-annotator literature asks for, so it is what is reported.

Two separate questions, and they are not the same one:

1. **Within-rater (test-retest).** The same model, same prompt, four independent reads of 200 comments.
   This is the instrument's own stability.
2. **Between-rater.** Claude and DeepSeek-V3 on all 3,366 comments under the identical prompt. This is
   whether the coding survives a change of model.

Each system is a separate binary variable (fired / did not fire in this comment), so alpha is computed
per system on nominal data. Reporting one number across all seven would hide that SEEKING is the
unstable one.
"""
import json
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def krippendorff_nominal(units):
    """units: list of lists of labels, one list per unit, one label per coder that coded it.

    Standard nominal alpha via the coincidence matrix. Units with fewer than two codings contribute
    nothing, which is the defined behaviour, not a shortcut.
    """
    coincidence = {}
    n_total = 0.0
    for vals in units:
        m = len(vals)
        if m < 2:
            continue
        for a, b in combinations(range(m), 2):
            for x, y in ((vals[a], vals[b]), (vals[b], vals[a])):
                coincidence[(x, y)] = coincidence.get((x, y), 0.0) + 1.0 / (m - 1)
        n_total += m
    if not coincidence:
        return float("nan")
    labels = sorted({c for pair in coincidence for c in pair})
    n_c = {c: sum(coincidence.get((c, k), 0.0) for k in labels) for c in labels}
    n = sum(n_c.values())
    if n <= 1:
        return float("nan")
    do = sum(coincidence.get((c, k), 0.0) for c in labels for k in labels if c != k)
    de = sum(n_c[c] * n_c[k] for c in labels for k in labels if c != k) / (n - 1)
    if de == 0:
        return float("nan")
    return 1.0 - do / de


def load_claude_by_id():
    out = {}
    for stage in ("stage1", "stage2", "stage3"):
        d = os.path.join(ROOT, "data", stage, "reads")
        for name in sorted(os.listdir(d)):
            if name.endswith(".reads.json"):
                for r in json.load(open(os.path.join(d, name))):
                    out[r["id"]] = r
    return out


def main():
    claude = load_claude_by_id()

    # ---- 1. within-rater, four reads of the noise sample
    ids = set(json.load(open(os.path.join(ROOT, "data/noise-sample-ids.json"))))
    rounds = {0: {i: claude[i] for i in ids if i in claude}}
    nd = os.path.join(ROOT, "data", "noise")
    for name in sorted(os.listdir(nd)):
        if name.endswith(".reads.json"):
            k = int(name[5])
            rounds.setdefault(k, {})
            for r in json.load(open(os.path.join(nd, name))):
                rounds[k][r["id"]] = r
    have = [i for i in ids if all(i in rounds[k] for k in rounds)]

    print("Krippendorff's alpha, nominal, per system")
    print("  binary variable per comment: did this system fire\n")
    print("  %-9s %-28s %s" % ("system", "within-rater (4 reads, n=%d)" % len(have), "between-rater (n=3365)"))

    ds = {}
    dd = os.path.join(ROOT, "data", "deepseek")
    for name in sorted(os.listdir(dd)):
        if name.endswith(".json"):
            for r in json.load(open(os.path.join(dd, name))):
                if not r.get("failed"):
                    ds[r["id"]] = r
    shared = [i for i in claude if i in ds]

    fired = {}
    for k in rounds:
        for i in have:
            fired[(k, i)] = rates.systems_fired(rounds[k][i])
    cl_f = {i: rates.systems_fired(claude[i]) for i in shared}
    ds_f = {i: rates.systems_fired(ds[i]) for i in shared}

    rows = {}
    for s in rates.SYSTEMS:
        within = krippendorff_nominal([[("y" if s in fired[(k, i)] else "n") for k in sorted(rounds)] for i in have])
        between = krippendorff_nominal([["y" if s in cl_f[i] else "n", "y" if s in ds_f[i] else "n"] for i in shared])
        rows[s] = (within, between)
        print("  %-9s %-28.3f %.3f" % (s, within, between))

    print("\n  conventional reading: alpha >= 0.80 is reliable, 0.67 to 0.80 supports tentative")
    print("  conclusions, below 0.67 is unreliable for that variable.")
    json.dump({s: {"within": rows[s][0], "between": rows[s][1]} for s in rows},
              open(os.path.join(ROOT, "data", "alpha.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
