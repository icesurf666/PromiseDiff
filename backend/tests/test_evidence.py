from app.documents import InspectedPdf, PageInfo
from app.evidence import validate_text_evidence
from app.schemas import DocumentTextEvidence


def test_invented_page_and_quote_are_rejected():
    docs = [InspectedPdf("x.pdf", (PageInfo(1, "Savings Goal Tracker", 1, 1),), False)]
    assert not validate_text_evidence(DocumentTextEvidence(filename="x.pdf", page=2, quote="Savings"), docs)
    assert not validate_text_evidence(DocumentTextEvidence(filename="x.pdf", page=1, quote="Made up"), docs)
