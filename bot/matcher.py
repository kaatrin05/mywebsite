from __future__ import annotations

import re

from .models import ContentCatalog


WORD_RE = re.compile(r"\w+", re.UNICODE)


def match_answer_key(content: ContentCatalog, text: str) -> str | None:
    lowered = text.lower()
    tokens = set(WORD_RE.findall(lowered))
    best_key = None
    best_score = 0
    for faq in content.faq:
        score = sum(1 for keyword in faq.keywords if keyword.lower() in lowered or keyword.lower() in tokens)
        if score > best_score:
            best_key = faq.answer_key
            best_score = score
    return best_key if best_score > 0 else None
