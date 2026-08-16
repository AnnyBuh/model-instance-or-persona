"""How much does reading a comment more than once buy?

    python3 analysis/ensemble_report.py

Uses the 200 comments that carry four independent reads. For each comment and system there are four
binary observations, so the instrument's own uncertainty about that comment is visible directly.

Three questions, in order of how much they matter:

1. **How much of the noise is genuine ambiguity?** If a system fires in 4 of 4 reads or 0 of 4, the
   instrument is sure. The split cases are where a rate can move.
2. **How much does majority voting stabilise a rate?** A single read gives one rate per round. A
   majority of 3 gives one rate per 3-read subset. Comparing the spread of each answers "would more
   reads have helped, and by how much".
3. **Does it buy back the withdrawn SEEKING claim?** That is the only finding lost to noise, so it is
   the concrete test of whether ensembling is worth the tokens.

No prompt change anywhere in here. This is the same instrument read more times.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {"A": "bereavement", "B": "consumer loss", "C": "AI loss"}


def load():
    ids = set(json.load(open(os.path.join(ROOT, "data/noise-sample-ids.json"))))
    rounds = {0: {}}
    for stage in ("stage1", "stage2", "stage3"):
        d = os.path.join(ROOT, "data", stage, "reads")
        for name in sorted(os.listdir(d)):
            if name.endswith(".reads.json"):
                for r in json.load(open(os.path.join(d, name))):
                    if r["id"] in ids:
                        rounds[0][r["id"]] = r
    nd = os.path.join(ROOT, "data", "noise")
    for name in sorted(os.listdir(nd)):
        if name.endswith(".reads.json"):
            n = int(name[5])
            rounds.setdefault(n, {})
            for r in json.load(open(os.path.join(nd, name))):
                rounds[n][r["id"]] = r
    cmap = {}
    for stage in ("stage1", "stage2", "stage3"):
        cmap.update({int(k): v for k, v in
                     json.load(open(os.path.join(ROOT, "data", stage, "corpus-map.json"))).items()})
    return sorted(ids), rounds, cmap


def main():
    ids, rounds, cmap = load()
    keys = sorted(rounds)
    fired = {(cid, s): sum(1 for r in keys if s in rates.systems_fired(rounds[r][cid]))
             for cid in ids for s in rates.SYSTEMS}

    print("1. where the noise actually lives, over %d comments x 7 systems" % len(ids))
    print("   a system is 'settled' when it fires in 0 of 4 or 4 of 4 reads\n")
    print("   %-8s %8s %8s %8s %8s %8s   %s" % ("system", "0/4", "1/4", "2/4", "3/4", "4/4", "unsettled"))
    for s in rates.SYSTEMS:
        counts = [sum(1 for cid in ids if fired[(cid, s)] == k) for k in range(5)]
        unsettled = sum(counts[1:4])
        print("   %-8s %8d %8d %8d %8d %8d   %5.1f%%"
              % (s, counts[0], counts[1], counts[2], counts[3], counts[4], 100.0 * unsettled / len(ids)))

    print("\n2. spread of rate(system, corpus), single read versus majority of 3")
    print("   single: one rate per read round, 4 of them")
    print("   majority of 3: fires when it appears in at least 2 of 3 reads, over all 4 subsets\n")
    triples = list(itertools.combinations(keys, 3))
    for corpus in ("A", "C", "B"):
        members = [cid for cid in ids if cmap[cid] == corpus]
        if len(members) < 20:
            print("   %s skipped, only %d comments in the sample" % (NAMES[corpus], len(members)))
            continue
        print("   %s (n=%d)" % (NAMES[corpus], len(members)))
        print("      %-8s %-22s %-22s %s" % ("system", "single read", "majority of 3", "spread cut"))
        for s in rates.SYSTEMS:
            single = [100.0 * sum(1 for cid in members if s in rates.systems_fired(rounds[r][cid])) / len(members)
                      for r in keys]
            maj = []
            for t in triples:
                k = sum(1 for cid in members
                        if sum(1 for r in t if s in rates.systems_fired(rounds[r][cid])) >= 2)
                maj.append(100.0 * k / len(members))
            ss, sm = max(single) - min(single), max(maj) - min(maj)
            if max(single) == 0 and max(maj) == 0:
                continue
            cut = "-" if ss == 0 else "%.0f%%" % (100 * (1 - sm / ss))
            print("      %-8s %5.1f to %5.1f (%4.1f)   %5.1f to %5.1f (%4.1f)   %s"
                  % (s, min(single), max(single), ss, min(maj), max(maj), sm, cut))

    print("\n3. does majority voting buy back the withdrawn SEEKING claim?")
    print("   the claim was: AI loss shows less SEEKING than consumer loss")
    print("   it was withdrawn because the gap, 9.6 points, is smaller than SEEKING's own spread\n")
    for label, sel in (("single read", None), ("majority of 3", triples)):
        gaps = []
        if sel is None:
            for r in keys:
                b = [cid for cid in ids if cmap[cid] == "B"]
                c = [cid for cid in ids if cmap[cid] == "C"]
                rb = sum(1 for cid in b if "seeking" in rates.systems_fired(rounds[r][cid])) / len(b)
                rc = sum(1 for cid in c if "seeking" in rates.systems_fired(rounds[r][cid])) / len(c)
                gaps.append(100 * (rb - rc))
        else:
            for t in sel:
                b = [cid for cid in ids if cmap[cid] == "B"]
                c = [cid for cid in ids if cmap[cid] == "C"]
                rb = sum(1 for cid in b if sum(1 for r in t if "seeking" in rates.systems_fired(rounds[r][cid])) >= 2) / len(b)
                rc = sum(1 for cid in c if sum(1 for r in t if "seeking" in rates.systems_fired(rounds[r][cid])) >= 2) / len(c)
                gaps.append(100 * (rb - rc))
        print("   %-14s gap B minus C: %s   range %.1f points, sign stable: %s"
              % (label, " ".join("%5.1f" % g for g in gaps), max(gaps) - min(gaps),
                 all(g > 0 for g in gaps) or all(g < 0 for g in gaps)))
    print("\n   note: only %d consumer-loss comments are in the noise sample, so this is indicative,"
          % len([cid for cid in ids if cmap[cid] == "B"]))
    print("   not a re-test. A real re-test needs the full corpora read k times.")


if __name__ == "__main__":
    main()
