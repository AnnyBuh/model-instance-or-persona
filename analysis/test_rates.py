"""Tests for the rate computation, written before the implementation.

The six assertions in PREREGISTRATION.md section 8, plus the validity filter the pilot forced on us
after DeepSeek was found emitting Hawkins levels in the systems field.

    python3 analysis/test_rates.py
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402


def read(cid, systems, altitude="Neutrality", segments=None):
    """One read in the instrument's output shape. `systems` is a list of (system, band)."""
    if segments is None:
        segments = [{"quote": "x", "four_sides": {}, "dominant": "factual",
                     "systems": [{"system": s, "band": b} for s, b in systems], "why": "Does a thing"}]
    return {"id": cid, "altitude": altitude, "segments": segments}


class TestValidity(unittest.TestCase):
    def test_invalid_system_labels_are_dropped_not_repaired(self):
        rs = [read(1, [("grief", "above"), ("neutrality", "above")])]
        clean, dropped = rates.validate(rs)
        self.assertEqual(rates.systems_fired(clean[0]), {"grief"})
        self.assertEqual(dropped["invalid_system"], 1)

    def test_unparseable_read_never_becomes_a_zero_row(self):
        """Assertion 6: a broken read is excluded from the denominator, not counted as no-fire."""
        rs = [read(1, [("grief", "above")]), {"id": 2, "broken": True}]
        clean, dropped = rates.validate(rs)
        self.assertEqual([r["id"] for r in clean], [1])
        self.assertEqual(dropped["unparseable"], 1)

    def test_invalid_band_is_dropped(self):
        rs = [read(1, [("grief", "sideways")])]
        clean, _ = rates.validate(rs)
        self.assertEqual(rates.systems_fired(clean[0]), set())


class TestRates(unittest.TestCase):
    def setUp(self):
        self.reads = [read(1, [("grief", "above")]), read(2, [("grief", "shutdown"), ("care", "above")]),
                      read(3, [("rage", "overwhelm")]), read(4, [])]
        self.corpus = {1: "A", 2: "A", 3: "A", 4: "A"}

    def test_rates_are_in_the_unit_interval(self):
        """Assertion 1."""
        out = rates.corpus_rates(self.reads, self.corpus)
        for system, r in out["A"]["rates"].items():
            self.assertGreaterEqual(r["rate"], 0.0, system)
            self.assertLessEqual(r["rate"], 1.0, system)
            self.assertLessEqual(r["lo"], r["rate"])
            self.assertLessEqual(r["rate"], r["hi"])

    def test_a_system_firing_twice_in_one_comment_counts_once(self):
        """The unit is the comment. Two segments both firing grief is still one comment."""
        two = read(9, [], segments=[
            {"quote": "a", "systems": [{"system": "grief", "band": "above"}], "why": ""},
            {"quote": "b", "systems": [{"system": "grief", "band": "overwhelm"}], "why": ""}])
        out = rates.corpus_rates([two], {9: "A"})
        self.assertEqual(out["A"]["rates"]["grief"]["n"], 1)
        self.assertEqual(out["A"]["read"], 1)

    def test_every_comment_counted_exactly_once_in_exactly_one_corpus(self):
        """Assertion 2."""
        corpus = {1: "A", 2: "A", 3: "B", 4: "B"}
        out = rates.corpus_rates(self.reads, corpus)
        self.assertEqual(sum(c["read"] for c in out.values()), len(self.reads))

    def test_denominator_is_the_corpus_size(self):
        out = rates.corpus_rates(self.reads, self.corpus)
        self.assertEqual(out["A"]["read"], 4)
        self.assertAlmostEqual(out["A"]["rates"]["grief"]["rate"], 0.5)
        self.assertAlmostEqual(out["A"]["rates"]["rage"]["rate"], 0.25)
        self.assertAlmostEqual(out["A"]["rates"]["lust"]["rate"], 0.0)

    def test_a_comment_with_no_systems_still_counts_in_the_denominator(self):
        out = rates.corpus_rates(self.reads, self.corpus)
        self.assertEqual(out["A"]["read"], 4)
        self.assertEqual(out["A"]["no_system"], 1)

    def test_unknown_comment_id_is_an_error_not_a_silent_drop(self):
        with self.assertRaises(KeyError):
            rates.corpus_rates(self.reads, {1: "A"})

    def test_bands_partition_the_firings_of_a_system(self):
        out = rates.corpus_rates(self.reads, self.corpus)
        g = out["A"]["bands"]["grief"]
        self.assertEqual(g["above"] + g["shutdown"] + g["overwhelm"], out["A"]["rates"]["grief"]["n"])


class TestWilson(unittest.TestCase):
    def test_interval_brackets_the_point_estimate(self):
        lo, hi = rates.wilson(30, 100)
        self.assertLess(lo, 0.30)
        self.assertGreater(hi, 0.30)

    def test_zero_count_has_a_zero_floor_and_a_positive_ceiling(self):
        lo, hi = rates.wilson(0, 50)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)

    def test_all_count_has_a_one_ceiling(self):
        lo, hi = rates.wilson(50, 50)
        self.assertEqual(hi, 1.0)
        self.assertLess(lo, 1.0)

    def test_more_data_narrows_the_interval(self):
        small = rates.wilson(5, 10)
        big = rates.wilson(50, 100)
        self.assertLess(big[1] - big[0], small[1] - small[0])

    def test_separation_is_non_overlap_of_intervals(self):
        self.assertTrue(rates.separated((60, 100), (10, 100)))
        self.assertFalse(rates.separated((50, 100), (48, 100)))


class TestLikesConserved(unittest.TestCase):
    def test_likes_are_conserved_across_a_per_system_split(self):
        """Assertion 5: splitting a corpus by system must not create or destroy likes."""
        likes = {1: 10, 2: 5, 3: 1, 4: 0}
        reads = [read(1, [("grief", "above")]), read(2, [("care", "above")]),
                 read(3, [("rage", "above")]), read(4, [])]
        total = rates.likes_total(reads, likes)
        by_system = rates.likes_by_system(reads, likes)
        self.assertEqual(total, 16)
        self.assertEqual(sum(by_system.values()) + rates.likes_unfired(reads, likes), total)


class TestCorpusTotalsMatchSource(unittest.TestCase):
    def test_corpus_totals_match_the_declared_thread_counts(self):
        """Assertion 3 and 4: totals reconcile against the collection record, exclusions counted."""
        with tempfile.TemporaryDirectory() as d:
            manifest = os.path.join(d, "m.json")
            json.dump({"A": {"threads": ["t1"], "scraped": 10, "contentless": 2}}, open(manifest, "w"))
            reads = [read(i, [("grief", "above")]) for i in range(8)]
            corpus = {i: "A" for i in range(8)}
            ok, detail = rates.reconcile(reads, corpus, json.load(open(manifest)))
            self.assertTrue(ok, detail)

    def test_reconcile_fails_loudly_when_counts_disagree(self):
        reads = [read(i, [("grief", "above")]) for i in range(5)]
        corpus = {i: "A" for i in range(5)}
        ok, detail = rates.reconcile(reads, corpus, {"A": {"threads": ["t1"], "scraped": 10, "contentless": 2}})
        self.assertFalse(ok)
        self.assertIn("A", detail)


if __name__ == "__main__":
    unittest.main(verbosity=2)
