"""Unit tests for backend.straico._extract_usage.

Pure dict-in, dict-out tests — no proxy server needed. Run from repo root:

    .venv/bin/python -m unittest test.test_extract_usage

Covers:
- Word-count extraction (the e01364b behavior — backfills missing coverage)
- Coin-price extraction (the new behavior in this PR)
- Independent fail-soft layering between the two
- Both v0 (`words`/`price`) and v1 (`overall_words`/`overall_price`) shapes
"""
import unittest

from backend.straico import _extract_usage


class ExtractUsageWordsTests(unittest.TestCase):
    """Backfill coverage for the words-as-tokens behavior added in e01364b."""

    def test_words_only_returns_token_counts_without_coins(self):
        resp = {
            "completion": {"choices": [{"message": {"content": "ok"}}]},
            "words": {"input": 4, "output": 1, "total": 5},
        }
        usage = _extract_usage(resp)
        self.assertEqual(usage["prompt_tokens"], 4)
        self.assertEqual(usage["completion_tokens"], 1)
        self.assertEqual(usage["total_tokens"], 5)
        self.assertNotIn("straico_coins", usage)

    def test_no_words_and_no_price_returns_none(self):
        resp = {"completion": {"choices": [{"message": {"content": "ok"}}]}}
        self.assertIsNone(_extract_usage(resp))

    def test_non_dict_input_returns_none(self):
        self.assertIsNone(_extract_usage(None))
        self.assertIsNone(_extract_usage("not a dict"))
        self.assertIsNone(_extract_usage(42))


class ExtractUsageCoinsTests(unittest.TestCase):
    """New behavior in this PR: surface Straico's coin price under usage."""

    def test_both_words_and_price_surface_together(self):
        resp = {
            "completion": {"choices": [{"message": {"content": "ok"}}]},
            "words": {"input": 4, "output": 1, "total": 5},
            "price": {"input": 0.16, "output": 0.04, "total": 0.20},
        }
        usage = _extract_usage(resp)
        # Words still extracted as before.
        self.assertEqual(usage["prompt_tokens"], 4)
        self.assertEqual(usage["completion_tokens"], 1)
        self.assertEqual(usage["total_tokens"], 5)
        # Coin price now surfaced under straico_coins, preserving per-direction split.
        self.assertIn("straico_coins", usage)
        self.assertAlmostEqual(usage["straico_coins"]["input"], 0.16)
        self.assertAlmostEqual(usage["straico_coins"]["output"], 0.04)
        self.assertAlmostEqual(usage["straico_coins"]["total"], 0.20)

    def test_malformed_price_leaves_words_intact(self):
        # Fail-soft: a bad `price` value must NOT invalidate word usage.
        for bad_price in ["not a dict", 42, None, {"input": "abc", "output": 0, "total": 0}]:
            with self.subTest(bad_price=bad_price):
                resp = {
                    "completion": {"choices": [{"message": {"content": "ok"}}]},
                    "words": {"input": 4, "output": 1, "total": 5},
                    "price": bad_price,
                }
                usage = _extract_usage(resp)
                self.assertIsNotNone(usage, f"words must still extract with price={bad_price!r}")
                self.assertEqual(usage["prompt_tokens"], 4)
                self.assertNotIn(
                    "straico_coins",
                    usage,
                    f"malformed price must not produce straico_coins (price={bad_price!r})",
                )

    def test_v1_overall_shape_surfaces_under_standard_field_names(self):
        # By symmetry with `words` → `overall_words` in e01364b. Defensive
        # coverage: scope-agent does not use the image (v1) path but the
        # tolerance prevents a follow-up if Straico ever shifts the default.
        resp = {
            "completions": {"model-x": {"completion": {"choices": [{"message": {"content": "ok"}}]}}},
            "overall_words": {"input": 4, "output": 1, "total": 5},
            "overall_price": {"input": 0.16, "output": 0.04, "total": 0.20},
        }
        usage = _extract_usage(resp)
        self.assertEqual(usage["total_tokens"], 5)
        self.assertAlmostEqual(usage["straico_coins"]["total"], 0.20)


if __name__ == "__main__":
    unittest.main()
