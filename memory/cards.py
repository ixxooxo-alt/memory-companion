"""Memory cards with character-bigram Jaccard dedupe."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_THRESHOLD = 0.6


def char_bigrams(text: str) -> set[str]:
    """Set of adjacent character pairs. Single leftover chars are kept as-is."""
    compact = "".join(text.split())
    if not compact:
        return set()
    if len(compact) == 1:
        return {compact}
    return {compact[i : i + 2] for i in range(len(compact) - 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


@dataclass
class MemoryCard:
    people: list[str] = field(default_factory=list)
    place: str = ""
    era: str = ""
    event: str = ""
    keywords: list[str] = field(default_factory=list)
    retell_count: int = 1

    def fingerprint(self) -> str:
        parts = list(self.people)
        parts.append(self.place)
        parts.append(self.era)
        parts.append(self.event)
        parts.extend(self.keywords)
        return "".join(parts)


class MemoryStore:
    """Holds memory cards and merges retellings above a Jaccard threshold."""

    def __init__(self, threshold: float = DEFAULT_THRESHOLD) -> None:
        self.threshold = threshold
        self.cards: list[MemoryCard] = []

    def __len__(self) -> int:
        return len(self.cards)

    def add(self, card: MemoryCard) -> MemoryCard:
        """Insert a new card, or merge it into the closest duplicate."""
        incoming = char_bigrams(card.fingerprint())
        best: MemoryCard | None = None
        best_score = -1.0
        for existing in self.cards:
            score = jaccard(incoming, char_bigrams(existing.fingerprint()))
            if score >= self.threshold and score > best_score:
                best = existing
                best_score = score
        if best is None:
            self.cards.append(card)
            return card
        self._merge(best, card)
        return best

    def _merge(self, target: MemoryCard, incoming: MemoryCard) -> None:
        target.retell_count += incoming.retell_count
        target.people = _unique(list(target.people) + list(incoming.people))
        target.keywords = _unique(list(target.keywords) + list(incoming.keywords))
        if not target.place and incoming.place:
            target.place = incoming.place
        if not target.era and incoming.era:
            target.era = incoming.era
        # Keep the first telling's event text; fill only if it was empty.
        if not target.event and incoming.event:
            target.event = incoming.event

    def save(self, path: str | Path) -> None:
        payload = [asdict(card) for card in self.cards]
        Path(path).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def load(self, path: str | Path) -> None:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        self.cards = [MemoryCard(**item) for item in payload]
