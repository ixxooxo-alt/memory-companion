"""Load a hotword list and fix near-miss typo variants in a transcript."""

from __future__ import annotations

from pathlib import Path

from asr.wer import levenshtein

DEFAULT_HOTWORDS_PATH = Path(__file__).with_name("hotwords.txt")


def load_hotwords(path: str | Path | None = None) -> list[str]:
    """Read non-empty, non-comment lines from a UTF-8 hotword file."""
    src = Path(path) if path is not None else DEFAULT_HOTWORDS_PATH
    words = []
    for line in src.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if item and not item.startswith("#"):
            words.append(item)
    return words


def _is_near_miss(window: str, hotword: str) -> bool:
    """True when window should be replaced by hotword (distance 0 or 1).

    Same-length windows only, so a match never swallows a neighboring
    character. For 2-character hotwords, the first character must match
    so common bigrams like '的茶' are not rewritten as '老茶'.
    """
    if len(window) != len(hotword):
        return False
    if window == hotword:
        return True
    if levenshtein(window, hotword) > 1:
        return False
    if len(hotword) <= 2 and window[0] != hotword[0]:
        return False
    return True


def apply_hotword_fix(text: str, hotwords: list[str]) -> str:
    """Replace same-length near-misses (edit distance <= 1) with hotwords.

    Longer hotwords are tried first. Scanning is greedy left to right.
    """
    if not text or not hotwords:
        return text
    words = sorted({w for w in hotwords if w}, key=len, reverse=True)
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        replaced = False
        for hw in words:
            wlen = len(hw)
            if wlen < 1 or i + wlen > n:
                continue
            window = text[i : i + wlen]
            if _is_near_miss(window, hw):
                out.append(hw)
                i += wlen
                replaced = True
                break
        if not replaced:
            out.append(text[i])
            i += 1
    return "".join(out)
