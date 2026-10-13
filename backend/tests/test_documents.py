from io import BytesIO

import fitz
import pytest

from app.documents import (
    A4,
    DocumentError,
    InspectedPdf,
    PageInfo,
    enforce_collection_limits,
    inspect_pdf,
    matches_size,
)


def pdf_bytes(encrypted: bool = False) -> bytes:
    document = fitz.open()
    document.new_page(width=841.89, height=595.28)
    stream = BytesIO()
    if encrypted:
        document.save(stream, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="owner", user_pw="user")
    else:
        document.save(stream)
    return stream.getvalue()


def test_detects_landscape_a4_and_rejects_invalid_pdf():
    pdf = inspect_pdf("a4.pdf", pdf_bytes())
    assert matches_size(pdf.pages[0], A4)
    with pytest.raises(DocumentError, match="valid PDF"):
        inspect_pdf("broken.pdf", b"not a pdf")


def test_rejects_encrypted_pdf():
    with pytest.raises(DocumentError, match="encrypted"):
        inspect_pdf("locked.pdf", pdf_bytes(encrypted=True))


def test_combined_page_limit_is_enforced():
    pages = tuple(PageInfo(number, "", 1, 1) for number in range(1, 162))
    with pytest.raises(DocumentError, match="Combined PDF page"):
        enforce_collection_limits([InspectedPdf("x.pdf", pages, False)])
