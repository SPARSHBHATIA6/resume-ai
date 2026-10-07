"""Text normalization and lightweight NLP helpers."""

import re
from collections import Counter
from typing import Iterable, List


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving useful punctuation."""
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_for_match(text: str) -> str:
    """Return lowercase text suitable for case-insensitive matching."""
    return re.sub(r"[^a-z0-9+#.\- ]+", " ", (text or "").lower())


def keyword_tokens(text: str) -> List[str]:
    """Extract simple alphanumeric keyword tokens."""
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", text or "")


def top_keywords(text: str, limit: int = 20) -> List[str]:
    """Return frequent non-trivial words for ATS-style analysis."""
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "your", "you",
        "are", "will", "have", "has", "our", "their", "they", "job", "role",
        "about", "into", "using", "looking", "work", "years", "team", "good",
        "skills", "experience", "required", "preferred", "ability", "knowledge",
    }
    words = [w.lower() for w in keyword_tokens(text) if w.lower() not in stopwords and len(w) > 2]
    return [word for word, _ in Counter(words).most_common(limit)]


def contains_phrase(text: str, phrase: str) -> bool:
    """Match a phrase as a word-aware substring."""
    return re.search(r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)", (text or "").lower()) is not None


def safe_join(items: Iterable[str]) -> str:
    """Join non-empty strings for reports/UI."""
    return ", ".join(str(item) for item in items if str(item).strip())
