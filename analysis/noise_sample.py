"""Build the noise re-read: 200 comments already read once, to be read three more times.

    python3 analysis/noise_sample.py <out_dir>

Design decisions that matter, because this is the test the whole result leans on:

- **Random across all corpora**, drawn with a fixed seed so the sample is reproducible from the repo
  rather than from my memory of what I did.
- **Three separate rounds**, written as three separate shard sets. A reader must never see the same
  comment twice in one context, because the second read would then be anchored on the first and the
  measured instability would be an underestimate, which is the flattering direction.
- **Same blind shape as the originals**: {id, text, post} only. No corpus label, no username, and
  nothing marking these as re-reads.
- Round shards are deliberately shuffled differently per round, so a comment does not sit in the same
  position or the same neighbourhood each time.
"""
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260816
N_SAMPLE = 200
ROUNDS = 3
PER_SHARD = 100


def load_pool():
    """Every comment that already has one read, with its text and post context."""
    pool = {}
    for stage in ("stage1", "stage2", "stage3"):
        path = os.path.join(ROOT, "data", stage, "%s-comments.json" % stage)
        if not os.path.exists(path):
            continue
        read_dir = os.path.join(ROOT, "data", stage, "reads")
        read_ids = set()
        if os.path.isdir(read_dir):
            for name in os.listdir(read_dir):
                if name.endswith(".reads.json"):
                    read_ids.update(r["id"] for r in json.load(open(os.path.join(read_dir, name))))
        for c in json.load(open(path)):
            if c["id"] in read_ids:
                pool[c["id"]] = c
    return pool


def main(out_dir):
    pool = load_pool()
    rng = random.Random(SEED)
    ids = sorted(pool)
    if len(ids) < N_SAMPLE:
        raise SystemExit("only %d comments have a first read; need %d" % (len(ids), N_SAMPLE))
    sample = rng.sample(ids, N_SAMPLE)

    by_corpus = {}
    for cid in sample:
        by_corpus[pool[cid]["corpus"]] = by_corpus.get(pool[cid]["corpus"], 0) + 1
    print("sampled %d comments, seed %d: %s" % (len(sample), SEED, by_corpus))

    os.makedirs(out_dir, exist_ok=True)
    json.dump(sorted(sample), open(os.path.join(ROOT, "data", "noise-sample-ids.json"), "w"))
    for r in range(1, ROUNDS + 1):
        order = list(sample)
        random.Random(SEED + r).shuffle(order)
        for i in range(0, len(order), PER_SHARD):
            chunk = order[i:i + PER_SHARD]
            name = "round%d-shard-%02d.json" % (r, i // PER_SHARD)
            json.dump([{"id": c, "text": pool[c]["text"], "post": pool[c]["post"]} for c in chunk],
                      open(os.path.join(out_dir, name), "w"), indent=0)
    print("wrote %d rounds x %d shards to %s" % (ROUNDS, -(-N_SAMPLE // PER_SHARD), out_dir))


if __name__ == "__main__":
    main(sys.argv[1])
