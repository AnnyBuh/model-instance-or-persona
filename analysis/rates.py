"""Rate computation for the affective map.

The unit of analysis is the COMMENT, never the segment and never a single read. A system either fired
in a comment or it did not, whatever number of segments it fired in. This is the whole reason the
study reports rates: the instrument disagrees with itself on roughly one comment in five, so a single
judgement carries no weight and only a rate over many comments does.

Definitions are fixed in PREREGISTRATION.md and must not drift:

    rate(system, corpus) = comments in which the system fired at least once / comments read

Confidence intervals are Wilson intervals at 90%, which behave at the boundaries where the normal
approximation does not, and several of these rates will sit near zero.
"""
import json
import math
import sys

SYSTEMS = ("seeking", "rage", "fear", "lust", "care", "grief", "play")
BANDS = ("above", "shutdown", "overwhelm")
Z90 = 1.6448536269514722  # two-sided 90%


# ----------------------------------------------------------------------------- validity

def _segments(r):
    segs = r.get("segments")
    return segs if isinstance(segs, list) else None


def validate(reads):
    """Split reads into usable ones and a tally of what was dropped and why.

    A read that cannot be parsed is EXCLUDED, never coerced into a comment that fired nothing. The
    difference matters: a zero row would quietly pull every rate down.
    """
    clean, dropped = [], {"unparseable": 0, "invalid_system": 0, "invalid_band": 0}
    for r in reads:
        segs = _segments(r)
        if segs is None or "id" not in r:
            dropped["unparseable"] += 1
            continue
        out_segs = []
        for s in segs:
            keep = []
            for f in s.get("systems") or []:
                if not isinstance(f, dict):
                    dropped["unparseable"] += 1
                    continue
                if f.get("system") not in SYSTEMS:
                    dropped["invalid_system"] += 1
                    continue
                if f.get("band") not in BANDS:
                    dropped["invalid_band"] += 1
                    continue
                keep.append(f)
            out_segs.append(dict(s, systems=keep))
        clean.append(dict(r, segments=out_segs))
    return clean, dropped


def systems_fired(read):
    """The set of systems that fired anywhere in this comment. The comment is the unit."""
    return {f["system"] for s in read.get("segments", []) for f in s.get("systems", [])
            if f.get("system") in SYSTEMS}


def bands_fired(read):
    """(system, band) pairs present in this comment, deduplicated within the comment."""
    return {(f["system"], f["band"]) for s in read.get("segments", []) for f in s.get("systems", [])
            if f.get("system") in SYSTEMS and f.get("band") in BANDS}


# ----------------------------------------------------------------------------- statistics

def wilson(k, n, z=Z90):
    """Wilson score interval. Returns (lo, hi), clamped to [0,1]."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def separated(a, b):
    """True when two (k, n) proportions have non-overlapping 90% intervals.

    This is the test the pre-registration commits to for anchor separation and for the placement
    claim. It is deliberately blunt: non-overlapping Wilson intervals, no hypothesis test, no p value
    to shop for.
    """
    la, ha = wilson(*a)
    lb, hb = wilson(*b)
    return ha < lb or hb < la


# ----------------------------------------------------------------------------- rates

def corpus_rates(reads, corpus_of, likes=None):
    """rate(system, corpus) for every system and corpus, with bands and Wilson intervals.

    `corpus_of` maps comment id to corpus label. A read whose id is not in the map raises, because a
    comment quietly falling out of every corpus is exactly the failure that inflates or deflates a
    rate without anyone noticing.
    """
    clean, dropped = validate(reads)
    out = {}
    for r in clean:
        cid = r["id"]
        if cid not in corpus_of:
            raise KeyError("comment %r belongs to no corpus" % (cid,))
        c = out.setdefault(corpus_of[cid], {
            "read": 0, "no_system": 0, "counts": {s: 0 for s in SYSTEMS},
            "bands": {s: {b: 0 for b in BANDS} for s in SYSTEMS}, "likes": 0})
        c["read"] += 1
        if likes:
            c["likes"] += likes.get(cid, 0)
        fired = systems_fired(r)
        if not fired:
            c["no_system"] += 1
        for s in fired:
            c["counts"][s] += 1
        seen = set()
        for s, b in bands_fired(r):
            if s in seen:
                continue  # one band per system per comment: the first, so bands partition the count
            seen.add(s)
            c["bands"][s][b] += 1
    for c in out.values():
        c["rates"] = {}
        for s in SYSTEMS:
            k, n = c["counts"][s], c["read"]
            lo, hi = wilson(k, n)
            c["rates"][s] = {"n": k, "of": n, "rate": (k / n if n else 0.0), "lo": lo, "hi": hi}
    return out


# ----------------------------------------------------------------------------- likes conservation

def likes_total(reads, likes):
    return sum(likes.get(r["id"], 0) for r in reads)


def likes_by_system(reads, likes):
    """Likes attributed to each system. A comment firing two systems contributes to both, so this
    sums to more than the total; the conservation test is on the UNFIRED remainder, not on this."""
    out = {s: 0 for s in SYSTEMS}
    for r in reads:
        for s in systems_fired(r):
            out[s] += likes.get(r["id"], 0)
    return out


def likes_unfired(reads, likes):
    return sum(likes.get(r["id"], 0) for r in reads if not systems_fired(r))


# ----------------------------------------------------------------------------- reconciliation

def reconcile(reads, corpus_of, manifest):
    """Assertion 3 and 4: corpus totals must equal what the collection record says was scraped,
    minus the documented exclusions. Returns (ok, detail)."""
    counted = {}
    for r in reads:
        counted[corpus_of[r["id"]]] = counted.get(corpus_of[r["id"]], 0) + 1
    detail = {}
    ok = True
    for corpus, m in manifest.items():
        expected = m["scraped"] - m.get("contentless", 0)
        got = counted.get(corpus, 0)
        detail[corpus] = {"expected": expected, "counted": got}
        if expected != got:
            ok = False
    return ok, detail


# ----------------------------------------------------------------------------- report

def report(reads, corpus_of, likes=None):
    clean, dropped = validate(reads)
    return {"corpora": corpus_rates(reads, corpus_of, likes=likes), "dropped": dropped,
            "n_reads_in": len(reads), "n_reads_used": len(clean)}


if __name__ == "__main__":
    reads = json.load(open(sys.argv[1]))
    corpus_of = {int(k): v for k, v in json.load(open(sys.argv[2])).items()}
    print(json.dumps(report(reads, corpus_of), indent=1))
