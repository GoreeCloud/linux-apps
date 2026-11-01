"""Text layout safeguards for unusually long unbroken strings.

GTK WORD_CHAR wrap can become expensive for pathological tokens. CHAR mode
preserves wrapping without attempting word-break detection on such tokens.
"""
from __future__ import annotations

FAST_WRAP_RUN = 4096


def needs_fast_wrap(text: str, threshold: int = FAST_WRAP_RUN) -> bool:
    """Return whether a token reaches the fast-character-wrap threshold."""
    if threshold < 1:
        raise ValueError("threshold must be positive")
    count = 0
    for character in text:
        if character.isspace():
            count = 0
        else:
            count += 1
            if count >= threshold:
                return True
    return False
