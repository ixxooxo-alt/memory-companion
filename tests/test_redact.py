"""Unit tests for PII redaction. All identifiers below are synthetic."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from privacy.redact import redact


class TestRedact(unittest.TestCase):
    def test_chinese_mobile(self):
        self.assertEqual(redact("电话是13812345678。"), "电话是[PHONE]。")

    def test_mobile_with_separators(self):
        self.assertEqual(redact("138-1234-5678"), "[PHONE]")
        self.assertEqual(redact("138 1234 5678"), "[PHONE]")

    def test_id_card(self):
        # Synthetic 18-digit pattern with a valid YYYYMMDD block.
        self.assertEqual(redact("证件110101199001011234"), "证件[ID]")
        self.assertEqual(redact("11010119900101123X"), "[ID]")

    def test_email(self):
        self.assertEqual(redact("写成 grandma@example.com 吧"), "写成 [EMAIL] 吧")

    def test_bank_card(self):
        self.assertEqual(redact("卡号6222021234567890"), "卡号[CARD]")
        self.assertEqual(redact("6222 0212 3456 7890"), "[CARD]")

    def test_mixed_sentence(self):
        text = (
            "有事打13812345678，或者发信到 someone@example.com，"
            "证件110101199001011234，卡6222021234567890123。"
        )
        got = redact(text)
        self.assertEqual(
            got,
            "有事打[PHONE]，或者发信到 [EMAIL]，证件[ID]，卡[CARD]。",
        )
        self.assertNotIn("13812345678", got)
        self.assertNotIn("someone@example.com", got)

    def test_leaves_ordinary_text_alone(self):
        text = "你看园子那盆你去年摘的茶花开得很透。"
        self.assertEqual(redact(text), text)

    def test_short_numbers_are_not_cards(self):
        self.assertEqual(redact("摘了3朵，一共12枝。"), "摘了3朵，一共12枝。")


if __name__ == "__main__":
    unittest.main()
