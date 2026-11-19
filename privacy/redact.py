"""Regex redaction of common Chinese PII patterns."""

from __future__ import annotations

import re

# 18-digit resident ID: area (6) + year (19xx/20xx) + month + day + seq (3) + check.
ID_RE = re.compile(
    r"(?<!\d)[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx](?!\d)"
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Mainland mobile: 1[3-9] plus 9 digits, optional space or dash separators.
PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d[ -]?\d{4}[ -]?\d{4}(?!\d)")
# Bank cards are typically 16–19 digits; applied after IDs so 18-digit IDs win.
CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){15,18}\d(?!\d)")


def redact(text: str) -> str:
    """Replace mobile numbers, IDs, emails, and bank cards with placeholders."""
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = ID_RE.sub("[ID]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    text = CARD_RE.sub("[CARD]", text)
    return text
