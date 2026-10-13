from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import fitz

MAX_PAGES = 160
MAX_TEXT = 200_000
A4 = (595.28, 841.89)
LETTER = (612.0, 792.0)
TOLERANCE = 3.0


class DocumentError(ValueError):
    pass


@dataclass(frozen=True)
class PageInfo:
    number: int
    text: str
    width: float
    height: float


@dataclass(frozen=True)
class InspectedPdf:
    filename: str
    pages: tuple[PageInfo, ...]
    has_forms: bool

    @property
    def page_count(self) -> int:
        return len(self.pages)


def inspect_pdf(filename: str, payload: bytes, page_limit: int = MAX_PAGES) -> InspectedPdf:
    if not payload.startswith(b"%PDF"):
        raise DocumentError(f"{filename} is not a valid PDF")
    try:
        document = fitz.open(stream=BytesIO(payload), filetype="pdf")
    except (fitz.FileDataError, RuntimeError) as exc:
        raise DocumentError(f"Could not read {filename}") from exc
    with document:
        if document.needs_pass:
            raise DocumentError(f"{filename} is encrypted or password-protected")
        if document.page_count > page_limit:
            raise DocumentError(f"PDF page limit ({page_limit}) exceeded")
        pages = []
        characters = 0
        for index, page in enumerate(document):
            text = page.get_text("text")
            characters += len(text)
            if characters > MAX_TEXT:
                raise DocumentError("Extracted text limit exceeded")
            rect = page.rect
            pages.append(PageInfo(index + 1, text, rect.width, rect.height))
        has_forms = any(page.first_widget is not None for page in document)
    return InspectedPdf(filename, tuple(pages), has_forms)


def matches_size(page: PageInfo, target: tuple[float, float]) -> bool:
    dimensions = sorted((page.width, page.height))
    expected = sorted(target)
    return all(abs(actual - wanted) <= TOLERANCE for actual, wanted in zip(dimensions, expected))


def has_complete_edition(pdf: InspectedPdf, target: tuple[float, float]) -> bool:
    return bool(pdf.pages) and all(matches_size(page, target) for page in pdf.pages)


def enforce_collection_limits(documents: list[InspectedPdf]) -> None:
    pages = sum(document.page_count for document in documents)
    text = sum(len(page.text) for document in documents for page in document.pages)
    if pages > MAX_PAGES:
        raise DocumentError(f"Combined PDF page limit ({MAX_PAGES}) exceeded")
    if text > MAX_TEXT:
        raise DocumentError("Combined extracted text limit exceeded")
