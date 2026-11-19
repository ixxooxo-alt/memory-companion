"""Unit tests for memory-card dedupe and JSON persistence."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from memory.cards import MemoryCard, MemoryStore, char_bigrams, jaccard


def _camellia_card(**overrides) -> MemoryCard:
    base = dict(
        people=["阿嬷"],
        place="园子",
        era="去年",
        event="你看园子那盆你去年摘的茶花开得很透。",
        keywords=["茶花", "园子"],
        retell_count=1,
    )
    base.update(overrides)
    return MemoryCard(**base)


class TestBigramJaccard(unittest.TestCase):
    def test_identical_strings(self):
        s = char_bigrams("茶花开得很透")
        self.assertEqual(jaccard(s, s), 1.0)

    def test_disjoint_strings(self):
        self.assertEqual(jaccard(char_bigrams("茶花"), char_bigrams("艾草")), 0.0)

    def test_empty_sets(self):
        self.assertEqual(jaccard(set(), set()), 1.0)
        self.assertEqual(jaccard(char_bigrams("茶花"), set()), 0.0)


class TestMemoryStore(unittest.TestCase):
    def test_first_card_is_stored(self):
        store = MemoryStore()
        card = store.add(_camellia_card())
        self.assertEqual(len(store), 1)
        self.assertEqual(card.retell_count, 1)

    def test_near_duplicate_is_merged(self):
        store = MemoryStore(threshold=0.6)
        store.add(_camellia_card())
        # Same story, slightly different wording and an extra keyword.
        merged = store.add(
            _camellia_card(
                event="你看园子那盆你去年摘的茶花开得很透",
                keywords=["茶花"],
                people=["阿嬷", "孙子"],
            )
        )
        self.assertEqual(len(store), 1)
        self.assertEqual(merged.retell_count, 2)
        self.assertIn("孙子", merged.people)
        self.assertIn("园子", merged.keywords)
        self.assertIn("茶花", merged.keywords)

    def test_unrelated_card_is_kept_separate(self):
        store = MemoryStore(threshold=0.6)
        store.add(_camellia_card())
        store.add(
            MemoryCard(
                people=["邻居"],
                place="菜市场",
                era="今年",
                event="清早去菜市场买青菜和豆腐。",
                keywords=["菜市场", "豆腐"],
            )
        )
        self.assertEqual(len(store), 2)
        self.assertEqual(store.cards[0].retell_count, 1)
        self.assertEqual(store.cards[1].retell_count, 1)

    def test_merge_fills_empty_place(self):
        store = MemoryStore()
        store.add(_camellia_card(place=""))
        store.add(_camellia_card(place="园子"))
        self.assertEqual(len(store), 1)
        self.assertEqual(store.cards[0].place, "园子")

    def test_save_and_load_roundtrip(self):
        store = MemoryStore()
        store.add(_camellia_card())
        store.add(_camellia_card(people=["阿嬷", "孙子"]))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cards.json"
            store.save(path)
            loaded = MemoryStore()
            loaded.load(path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded.cards[0].retell_count, 2)
        self.assertEqual(loaded.cards[0].people, ["阿嬷", "孙子"])
        self.assertEqual(loaded.cards[0].event, "你看园子那盆你去年摘的茶花开得很透。")


if __name__ == "__main__":
    unittest.main()
