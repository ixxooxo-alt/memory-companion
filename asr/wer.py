"""Character-level error rate for Chinese (and mixed) transcripts.

This is a scoring utility. It does not run an ASR model.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path


def normalize(text: str) -> str:
    """Drop whitespace, punctuation, and symbols; keep letters, digits, and CJK."""
    chars = []
    for ch in text:
        if ch.isspace():
            continue
        cat = unicodedata.category(ch)
        if cat.startswith("P") or cat.startswith("S"):
            continue
        chars.append(ch)
    return "".join(chars)


def levenshtein(a: str, b: str) -> int:
    """Classic edit distance (insert / delete / substitute)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    # Previous and current DP rows; columns are characters of b.
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            ins = curr[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            curr.append(min(ins, delete, sub))
        prev = curr
    return prev[-1]


def cer(ref: str, hyp: str) -> float:
    """Character error rate: edit distance / len(normalized ref).

    Both strings are normalized (punctuation and whitespace removed)
    before scoring. Returns 0.0 when both are empty; 1.0 when the
    reference is empty but the hypothesis is not.
    """
    ref_n = normalize(ref)
    hyp_n = normalize(hyp)
    if not ref_n:
        return 0.0 if not hyp_n else 1.0
    return levenshtein(ref_n, hyp_n) / len(ref_n)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Character error rate between a reference and a hypothesis file."
    )
    parser.add_argument("ref", type=Path, help="Reference transcript (UTF-8)")
    parser.add_argument("hyp", type=Path, help="Hypothesis transcript (UTF-8)")
    args = parser.parse_args(argv)

    ref = args.ref.read_text(encoding="utf-8")
    hyp = args.hyp.read_text(encoding="utf-8")
    ref_n = normalize(ref)
    hyp_n = normalize(hyp)
    edits = levenshtein(ref_n, hyp_n)
    score = cer(ref, hyp)

    sys.stdout.write(
        f"CER: {score:.4f}\n"
        f"edits: {edits}\n"
        f"ref_chars: {len(ref_n)}\n"
        f"hyp_chars: {len(hyp_n)}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
