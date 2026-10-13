from __future__ import annotations

import re

from .documents import InspectedPdf
from .schemas import Claim


def document_index(documents: list[InspectedPdf], per_page: int = 600) -> str:
    rows = []
    for document in documents:
        for page in document.pages:
            text = re.sub(r"\s+", " ", page.text).strip()[:per_page]
            rows.append(f"[{document.filename} p.{page.number}] {text}")
    return "\n".join(rows)


def excerpts(documents: list[InspectedPdf], references: list[tuple[str, int]]) -> str:
    selected = []
    for filename, page_number in references:
        for document in documents:
            if document.filename == filename and 0 < page_number <= document.page_count:
                selected.append(f"[{filename} p.{page_number}] {document.pages[page_number - 1].text[:2500]}")
    return "\n".join(selected)


def semantic_candidates(claims: list[Claim], documents: list[InspectedPdf]) -> list[tuple[str, int]]:
    words = {
        word.lower()
        for claim in claims
        for word in re.findall(r"[a-zA-Z]{4,}", claim.text)
        if word.lower() not in {"includes", "contains", "with", "from", "that"}
    }
    ranked = []
    for document in documents:
        for page in document.pages:
            text = page.text.lower()
            score = sum(word in text for word in words)
            if score:
                ranked.append((score, document.filename, page.number))
    ranked.sort(reverse=True)
    selected = [(filename, number) for _, filename, number in ranked[:12]]
    if selected:
        return selected
    return [(document.filename, page.number) for document in documents for page in document.pages[:3]]
