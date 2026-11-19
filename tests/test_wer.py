"""Unit tests for character-level CER. No ASR model is run here."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from asr.wer import cer, levenshtein, normalize

GRANDMA_REF = "你看园子那盆你去年摘的茶花开得很透。"


class TestNormalize(unittest.TestCase):
    def test_strips_punctuation_and_whitespace(self):
        self.assertEqual(normalize("你好， 世界！"), "你好世界")

    def test_keeps_cjk_and_letters(self):
        self.assertEqual(normalize("茶花 camellia"), "茶花camellia")


class TestLevenshtein(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(levenshtein("茶花", "茶花"), 0)

    def test_one_substitution(self):
        self.assertEqual(levenshtein("茶花", "茶华"), 1)

    def test_insertion_and_deletion(self):
        self.assertEqual(levenshtein("茶花", "茶"), 1)
        self.assertEqual(levenshtein("茶", "茶花"), 1)


class TestCer(unittest.TestCase):
    def test_exact_match_is_zero(self):
        self.assertEqual(cer("你好世界", "你好世界"), 0.0)

    def test_one_substitution_over_four_chars(self):
        self.assertEqual(cer("你好世界", "你好世届"), 0.25)

    def test_ignores_punctuation(self):
        self.assertEqual(cer("你好，世界。", "你好世界"), 0.0)

    def test_empty_both(self):
        self.assertEqual(cer("", ""), 0.0)
        self.assertEqual(cer("……", "   "), 0.0)

    def test_empty_ref_nonzero_hyp(self):
        self.assertEqual(cer("", "你好"), 1.0)

    def test_grandma_ref_punct_only_difference(self):
        hyp = "你看园子那盆你去年摘的茶花开得很透"
        self.assertEqual(cer(GRANDMA_REF, hyp), 0.0)

    def test_grandma_ref_one_known_substitution(self):
        # 17 characters after normalization; one substitution -> 1/17.
        hyp = "你看园子那盆你去年摘的茶华开得很透。"
        self.assertEqual(len(normalize(GRANDMA_REF)), 17)
        self.assertAlmostEqual(cer(GRANDMA_REF, hyp), 1 / 17)


class TestWerCli(unittest.TestCase):
    def test_cli_prints_zero_cer_for_matching_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref = Path(tmp) / "ref.txt"
            hyp = Path(tmp) / "hyp.txt"
            ref.write_text(GRANDMA_REF, encoding="utf-8")
            hyp.write_text("你看园子那盆你去年摘的茶花开得很透", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "asr.wer", str(ref), str(hyp)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertIn("CER: 0.0000", result.stdout)
        self.assertIn("edits: 0", result.stdout)
        self.assertIn("ref_chars: 17", result.stdout)


if __name__ == "__main__":
    unittest.main()
