"""Aggregate the stage-1 reads and apply the allocation rules.

    python3 analysis/stage1_report.py <reads_dir> [out.json]

Prints the seven-system table with 90% Wilson intervals, the band split, and then evaluates R1, R2
and R4 from PREREGISTRATION.md section 4. The rules are evaluated in code so the allocation decision
is a consequence of the numbers rather than a judgement made after seeing them.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {"A": "bereavement", "B": "consumer loss", "C": "AI loss"}


def load_reads(reads_dir):
    out = []
    for name in sorted(os.listdir(reads_dir)):
        if name.endswith(".reads.json"):
            out.extend(json.load(open(os.path.join(reads_dir, name))))
    return out


def main(reads_dir, out_path=None):
    reads = load_reads(reads_dir)
    corpus_of = {int(k): v for k, v in json.load(open(os.path.join(ROOT, "data/stage1/corpus-map.json"))).items()}
    likes = {int(k): v for k, v in json.load(open(os.path.join(ROOT, "data/stage1/likes.json"))).items()}
    manifest = json.load(open(os.path.join(ROOT, "data/stage1/manifest.json")))

    rep = rates.report(reads, corpus_of, likes=likes)
    corpora = rep["corpora"]

    ok, detail = rates.reconcile(*rates.validate(reads)[:1] + (corpus_of, manifest))
    print("reconciliation against the collection record: %s" % ("ok" if ok else "MISMATCH"))
    for c, d in sorted(detail.items()):
        print("   %s %-14s expected %4d  counted %4d" % (c, NAMES[c], d["expected"], d["counted"]))
    print("reads in %d, used %d, dropped %s\n" % (rep["n_reads_in"], rep["n_reads_used"], rep["dropped"]))

    print("rate(system, corpus), 90% Wilson intervals")
    print("%-9s %s" % ("", "".join("%-22s" % NAMES[c] for c in "ABC" if c in corpora)))
    for s in rates.SYSTEMS:
        row = "%-9s" % s
        for c in "ABC":
            if c not in corpora:
                continue
            r = corpora[c]["rates"][s]
            row += "%5.1f%% [%4.1f,%4.1f]   " % (100 * r["rate"], 100 * r["lo"], 100 * r["hi"])
        print(row)
    print()
    for c in "ABC":
        if c not in corpora:
            continue
        cc = corpora[c]
        print("%-14s n=%3d  no system fired: %d  likes: %d" % (NAMES[c], cc["read"], cc["no_system"], cc["likes"]))

    print("\nband split, share of each system's firings")
    for c in "ABC":
        if c not in corpora:
            continue
        print("  %s" % NAMES[c])
        for s in rates.SYSTEMS:
            b = corpora[c]["bands"][s]
            tot = sum(b.values())
            if tot:
                print("    %-8s above %3d  shutdown %3d  overwhelm %3d" % (s, b["above"], b["shutdown"], b["overwhelm"]))

    # ------------------------------------------------------------------ the pre-registered rules
    decisions = {}
    if all(c in corpora for c in "AB"):
        ga = (corpora["A"]["counts"]["grief"], corpora["A"]["read"])
        gb = (corpora["B"]["counts"]["grief"], corpora["B"]["read"])
        sep = rates.separated(ga, gb)
        decisions["R1_anchors_separate_on_grief"] = sep
        print("\nR1: anchors separate on GRIEF with non-overlapping 90%% intervals: %s" % sep)
        print("    A grief %d/%d  %s" % (ga[0], ga[1], tuple(round(100 * x, 1) for x in rates.wilson(*ga))))
        print("    B grief %d/%d  %s" % (gb[0], gb[1], tuple(round(100 * x, 1) for x in rates.wilson(*gb))))
        if "C" in corpora:
            gc = (corpora["C"]["counts"]["grief"], corpora["C"]["read"])
            print("    C grief %d/%d  %s" % (gc[0], gc[1], tuple(round(100 * x, 1) for x in rates.wilson(*gc))))
            above_b = rates.separated(gc, gb)
            below_a = rates.separated(gc, ga)
            decisions["placement_C_above_B"] = above_b
            decisions["placement_C_below_A"] = below_a
            ra, rb, rc = [corpora[x]["rates"]["grief"]["rate"] for x in "ABC"]
            decisions["closer_to_B_than_A"] = abs(rc - rb) < abs(rc - ra)
            print("    C above B: %s   C below A: %s   closer to B: %s"
                  % (above_b, below_a, decisions["closer_to_B_than_A"]))
        widths = {c: (lambda r: r["hi"] - r["lo"])(corpora[c]["rates"]["grief"]) for c in corpora}
        decisions["widest_grief_interval"] = max(widths, key=widths.get)
        print("    widest GRIEF interval: %s (R2 and R4 send the next sample there)"
              % NAMES[decisions["widest_grief_interval"]])

    if out_path:
        json.dump({"report": rep, "decisions": decisions}, open(out_path, "w"), indent=1)
        print("\nwrote %s" % out_path)
    return rep, decisions


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
