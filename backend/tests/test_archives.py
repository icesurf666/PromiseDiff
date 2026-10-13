from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from app.archives import ArchiveError, unpack_pdfs


def archive(entries: list[tuple[str, bytes]]) -> bytes:
    stream = BytesIO()
    with ZipFile(stream, "w", ZIP_DEFLATED) as bundle:
        for name, content in entries:
            bundle.writestr(name, content)
    return stream.getvalue()


def test_rejects_traversal_and_non_pdf_members():
    with pytest.raises(ArchiveError, match="unsafe"):
        unpack_pdfs(archive([("../secret.pdf", b"%PDF-1.7")]))
    with pytest.raises(ArchiveError, match="PDF files only"):
        unpack_pdfs(archive([("notes.txt", b"nope")]))


def test_returns_pdf_members_without_extracting_to_disk():
    members = unpack_pdfs(archive([("nested/planner.pdf", b"%PDF-1.7")]))
    assert members == [("planner.pdf", b"%PDF-1.7")]


def test_rejects_duplicate_and_highly_compressed_members():
    with pytest.raises(ArchiveError, match="duplicate"):
        unpack_pdfs(archive([("one.pdf", b"%PDF-1.7"), ("one.pdf", b"%PDF-1.7")]))
    with pytest.raises(ArchiveError, match="decompression"):
        unpack_pdfs(archive([("large.pdf", b"0" * 1_000_000)]))
