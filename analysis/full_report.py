"""The whole study in one table: every corpus, every stage, every read.

    python3 analysis/full_report.py [out.json]

Loads every committed read across stage 1, 2 and 3, reconciles each corpus against its collection
record, then reports rate(system, corpus) with 90% Wilson intervals, the band split, and the
pre-registered decisions. Unlike stage1_report.py this takes the corpus map from all stages, so it is
the one to run once reading is finished.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {"A": "bereavement", "B": "consumer loss", "C": "AI loss"}
STAGES = ("stage1", "stage2", "stage3")


def load_all():
    reads, cmap, likes, manifest, threads = [], {}, {}, {}, {}
    for stage in STAGES:
        d = os.path.join(ROOT, "data", stage)
        if not os.path.isdir(d):
            continue
        rd = os.path.join(d, "reads")
        if os.path.isdir(rd):
            for name in sorted(os.listdir(rd)):
                if name.endswith(".reads.json"):
                    reads.extend(json.load(open(os.path.join(rd, name))))
        p = os.path.join(d, "corpus-map.json")
        if os.path.exists(p):
            cmap.update({int(k): v for k, v in json.load(open(p)).items()})
        p = os.path.join(d, "likes.json")
        if os.path.exists(p):
            likes.update({int(k): v for k, v in json.load(open(p)).items()})
        p = os.path.join(d, "manifest.json")
        if os.path.exists(p):
            for corpus, m in json.load(open(p)).items():
                agg = manifest.setdefault(corpus, {"threads": [], "scraped": 0, "contentless": 0})
                agg["threads"] += m["threads"]
                agg["scraped"] += m["scraped"]
                agg["contentless"] += m.get("contentless", 0)
        p = os.path.join(d, "%s-comments.json" % stage)
        if os.path.exists(p):
            for c in json.load(open(p)):
                threads[c["id"]] = c["thread"]
    return reads, cmap, likes, manifest, threads


def main(out_path=None):
    reads, cmap, likes, manifest, threads = load_all()
    dupes = len(reads) - len({r["id"] for r in reads})
    print("reads loaded: %d  (duplicate ids: %d)" % (len(reads), dupes))

    ok, detail = rates.reconcile(rates.validate(reads)[0], cmap, manifest)
    print("reconciliation: %s" % ("ok" if ok else "MISMATCH"))
    for c, d in sorted(detail.items()):
        print("   %s %-14s expected %5d  counted %5d  (%d threads)"
              % (c, NAMES[c], d["expected"], d["counted"], len(manifest[c]["threads"])))

    rep = rates.report(reads, cmap, likes=likes)
    corpora = rep["corpora"]
    print("   dropped: %s\n" % rep["dropped"])

    print("rate(system, corpus), 90% Wilson intervals")
    header = "".join("%-24s" % ("%s (n=%d)" % (NAMES[c], corpora[c]["read"])) for c in "ABC" if c in corpora)
    print("%-9s %s" % ("", header))
    for s in rates.SYSTEMS:
        row = "%-9s" % s
        for c in "ABC":
            if c in corpora:
                r = corpora[c]["rates"][s]
                row += "%5.1f%% [%4.1f,%4.1f]     " % (100 * r["rate"], 100 * r["lo"], 100 * r["hi"])
        print(row)

    print("\nband split, comments in which the system fired, by band")
    for c in "ABC":
        if c not in corpora:
            continue
        print("  %s" % NAMES[c])
        for s in rates.SYSTEMS:
            b = corpora[c]["bands"][s]
            if sum(b.values()):
                print("    %-8s above %4d  shutdown %3d  overwhelm %3d" % (s, b["above"], b["shutdown"], b["overwhelm"]))

    out = {"corpora": corpora, "dropped": rep["dropped"], "n_reads": len(reads), "decisions": {}}
    if all(c in corpora for c in "ABC"):
        g = {c: (corpora[c]["counts"]["grief"], corpora[c]["read"]) for c in "ABC"}
        print("\nthe pre-registered placement, on GRIEF")
        for c in "ABC":
            lo, hi = rates.wilson(*g[c])
            print("   %-14s %4d/%-5d %5.1f%%  [%4.1f, %4.1f]"
                  % (NAMES[c], g[c][0], g[c][1], 100 * g[c][0] / g[c][1], 100 * lo, 100 * hi))
        d = out["decisions"]
        d["anchors_separate"] = rates.separated(g["A"], g["B"])
        d["C_above_B"] = rates.separated(g["C"], g["B"])
        d["C_below_A"] = rates.separated(g["C"], g["A"])
        r = {c: g[c][0] / g[c][1] for c in "ABC"}
        d["closer_to_B"] = abs(r["C"] - r["B"]) < abs(r["C"] - r["A"])
        print("   anchors separate: %(anchors_separate)s | C above B: %(C_above_B)s | "
              "C below A: %(C_below_A)s | closer to B: %(closer_to_B)s" % d)
        print("\nthe hybrid prediction, which was that AI loss carries consumer-loss levels of RAGE and")
        print("elevated CARE:")
        for s in ("rage", "care", "seeking"):
            gs = {c: (corpora[c]["counts"][s], corpora[c]["read"]) for c in "BC"}
            same = not rates.separated(gs["B"], gs["C"])
            print("   %-8s B %5.1f%%  C %5.1f%%  intervals overlap: %s"
                  % (s, 100 * gs["B"][0] / gs["B"][1], 100 * gs["C"][0] / gs["C"][1], same))
            out["decisions"]["hybrid_%s_overlap" % s] = same

    if out_path:
        json.dump(out, open(out_path, "w"), indent=1)
        print("\nwrote %s" % out_path)
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
