"""Check a shard of reads against the shard of comments it was supposed to read.

A reader that quietly drops comments, invents ids, or paraphrases a quote would move every rate
downstream, and none of that shows up in the numbers themselves. So it is checked here, per shard,
before anything is aggregated.

    python3 analysis/validate_reads.py <shards_dir> <reads_dir>
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402


def check(shard_path, reads_path):
    shard = json.load(open(shard_path))
    reads = json.load(open(reads_path))
    by_id = {c["id"]: c for c in shard}
    problems = []

    if len(reads) != len(shard):
        problems.append("count: %d reads for %d comments" % (len(reads), len(shard)))

    seen = set()
    for r in reads:
        cid = r.get("id")
        if cid not in by_id:
            problems.append("id %r not in shard" % (cid,))
            continue
        if cid in seen:
            problems.append("id %r read twice" % (cid,))
        seen.add(cid)
        text = by_id[cid]["text"]
        for s in r.get("segments") or []:
            q = s.get("quote", "")
            if q and q not in text:
                problems.append("id %s: quote not a substring: %r" % (cid, q[:60]))
            for f in s.get("systems") or []:
                if f.get("system") not in rates.SYSTEMS:
                    problems.append("id %s: invalid system %r" % (cid, f.get("system")))
                if f.get("band") not in rates.BANDS:
                    problems.append("id %s: invalid band %r" % (cid, f.get("band")))
        if r.get("altitude") in (None, ""):
            problems.append("id %s: no altitude" % (cid,))

    missing = set(by_id) - seen
    if missing:
        problems.append("%d comments never read: %s" % (len(missing), sorted(missing)[:8]))
    return problems


if __name__ == "__main__":
    shards_dir, reads_dir = sys.argv[1], sys.argv[2]
    total_problems = 0
    for name in sorted(os.listdir(reads_dir)):
        if not name.endswith(".reads.json"):
            continue
        shard = os.path.join(shards_dir, name.replace(".reads.json", ".json"))
        probs = check(shard, os.path.join(reads_dir, name))
        total_problems += len(probs)
        print("%-24s %s" % (name, "clean" if not probs else "%d problems" % len(probs)))
        for p in probs[:6]:
            print("    " + p)
    sys.exit(1 if total_problems else 0)
