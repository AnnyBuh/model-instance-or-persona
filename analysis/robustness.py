"""Is the result carried by one thread?

    python3 analysis/robustness.py

Every corpus here is a handful of threads, and threads are not independent samples: one viral post
with 400 replies can dominate a rate, and if that post happens to be unusual the whole finding is
about it. So every rate is recomputed with each thread removed in turn, and the placement conditions
are re-tested each time.

Nothing is re-read. This is arithmetic over reads already committed.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {"A": "bereavement", "B": "consumer loss", "C": "AI loss"}


def load():
    reads, cmap, thread = [], {}, {}
    for stage in ("stage1", "stage2", "stage3"):
        d = os.path.join(ROOT, "data", stage)
        for name in sorted(os.listdir(os.path.join(d, "reads"))):
            if name.endswith(".reads.json"):
                reads.extend(json.load(open(os.path.join(d, "reads", name))))
        cmap.update({int(k): v for k, v in json.load(open(os.path.join(d, "corpus-map.json"))).items()})
        for c in json.load(open(os.path.join(d, "%s-comments.json" % stage))):
            thread[c["id"]] = c["thread"]
    return reads, cmap, thread


def grief(reads, cmap):
    r = rates.corpus_rates(reads, cmap)
    return {c: (r[c]["counts"]["grief"], r[c]["read"]) for c in "ABC" if c in r}


def main():
    reads, cmap, thread = load()
    base = grief(reads, cmap)
    print("all threads: A %.1f%%  C %.1f%%  B %.1f%%"
          % tuple(100 * base[c][0] / base[c][1] for c in "ACB"))

    threads = sorted({thread[r["id"]] for r in reads})
    print("\nleave one thread out, %d threads, GRIEF rate and whether every placement condition holds"
          % len(threads))
    worst = None
    for t in threads:
        sub = [r for r in reads if thread[r["id"]] != t]
        g = grief(sub, cmap)
        if len(g) < 3:
            continue
        ok = (rates.separated(g["C"], g["B"]) and rates.separated(g["C"], g["A"])
              and abs(g["C"][0] / g["C"][1] - g["B"][0] / g["B"][1])
              < abs(g["C"][0] / g["C"][1] - g["A"][0] / g["A"][1]))
        corpus = cmap[[r["id"] for r in reads if thread[r["id"]] == t][0]]
        drop = sum(1 for r in reads if thread[r["id"]] == t)
        line = ("   %-9s %-22s n-%-4d  A %5.1f  C %5.1f  B %5.1f   placement holds: %s"
                % (NAMES[corpus], t, drop, 100 * g["A"][0] / g["A"][1],
                   100 * g["C"][0] / g["C"][1], 100 * g["B"][0] / g["B"][1], ok))
        print(line)
        if not ok:
            worst = line
    print("\nplacement fails when any single thread is removed: %s" % ("YES, see above" if worst else "no"))


if __name__ == "__main__":
    main()
