"""Measure how much the instrument disagrees with itself, and compare that to the claimed gaps.

    python3 analysis/noise_report.py <noise_reads_dir>

Every comment in the noise sample has four independent reads: its original one plus three re-reads.
Three numbers come out, and they answer three different objections:

1. **exact instability** - the share of comments whose SET of systems is not identical across all four
   reads. This is the headline "one comment in N differs" figure, and it is deliberately harsh: one
   system appearing in one read out of four counts the comment as unstable.
2. **per-system flip rate** - for each system separately, the share of comments where it fired in some
   reads and not others. This is what actually matters for a rate, because a rate is computed per
   system, and a comment flipping between PLAY and SEEKING does not move the GRIEF rate at all.
3. **rate spread across rounds** - recompute rate(system, corpus) from each round separately. The
   spread between rounds is the honest error bar on the instrument, and the claim survives only if the
   corpus gaps are wider than it.

Number 3 is the one to lead with. Numbers 1 and 2 are how the instrument is described; number 3 is
whether the finding holds.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {"A": "bereavement", "B": "consumer loss", "C": "AI loss"}


def load_original_reads(ids):
    out = {}
    for stage in ("stage1", "stage2", "stage3"):
        d = os.path.join(ROOT, "data", stage, "reads")
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".reads.json"):
                continue
            for r in json.load(open(os.path.join(d, name))):
                if r["id"] in ids:
                    out[r["id"]] = r
    return out


def corpus_map():
    m = {}
    for stage in ("stage1", "stage2", "stage3"):
        p = os.path.join(ROOT, "data", stage, "corpus-map.json")
        if os.path.exists(p):
            m.update({int(k): v for k, v in json.load(open(p)).items()})
    return m


def main(noise_dir):
    ids = set(json.load(open(os.path.join(ROOT, "data", "noise-sample-ids.json"))))
    cmap = corpus_map()

    rounds = {0: load_original_reads(ids)}
    for name in sorted(os.listdir(noise_dir)):
        if not name.endswith(".reads.json") or not name.startswith("round"):
            continue
        r = int(name[5])
        rounds.setdefault(r, {})
        for read in json.load(open(os.path.join(noise_dir, name))):
            rounds[r][read["id"]] = read

    have = [cid for cid in ids if all(cid in rounds[r] for r in rounds)]
    print("comments with all %d reads: %d of %d" % (len(rounds), len(have), len(ids)))

    # 1 - exact instability
    unstable = 0
    for cid in have:
        sets = [frozenset(rates.systems_fired(rounds[r][cid])) for r in sorted(rounds)]
        if len(set(sets)) > 1:
            unstable += 1
    print("\n1. exact instability: %d of %d comments (%.0f%%) do not give the identical system set "
          "across all %d reads" % (unstable, len(have), 100.0 * unstable / max(1, len(have)), len(rounds)))

    # 2 - per-system flip rate
    print("\n2. per-system flip rate, the share of comments where the system fires in some reads but not others")
    for s in rates.SYSTEMS:
        flips = 0
        for cid in have:
            fired = [s in rates.systems_fired(rounds[r][cid]) for r in sorted(rounds)]
            if any(fired) and not all(fired):
                flips += 1
        print("   %-8s %4d of %d  %5.1f%%" % (s, flips, len(have), 100.0 * flips / max(1, len(have))))

    # 3 - rate spread across rounds
    print("\n3. rate(system, corpus) recomputed from each read round separately, on this 200-comment sample")
    per_round = {}
    for r in sorted(rounds):
        reads = [rounds[r][cid] for cid in have]
        per_round[r] = rates.corpus_rates(reads, {cid: cmap[cid] for cid in have})
    for corpus in ("A", "B", "C"):
        if corpus not in per_round[0]:
            continue
        print("   %s (n=%d)" % (NAMES[corpus], per_round[0][corpus]["read"]))
        for s in rates.SYSTEMS:
            vals = [100 * per_round[r][corpus]["rates"][s]["rate"] for r in sorted(rounds) if corpus in per_round[r]]
            if max(vals) == 0:
                continue
            print("      %-8s %s   spread %.1f points" %
                  (s, "  ".join("%5.1f" % v for v in vals), max(vals) - min(vals)))
    return per_round


if __name__ == "__main__":
    main(sys.argv[1])
