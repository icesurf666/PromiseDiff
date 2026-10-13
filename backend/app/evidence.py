from __future__ import annotations

import re

from .documents import InspectedPdf
from .schemas import DocumentTextEvidence


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def validate_text_evidence(evidence: DocumentTextEvidence, documents: list[InspectedPdf]) -> bool:
    if not evidence.quote.strip():
        return False
    for document in documents:
        if document.filename == evidence.filename and evidence.page <= document.page_count:
            return normalize(evidence.quote) in normalize(document.pages[evidence.page - 1].text)
    return False
