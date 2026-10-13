from app.documents import A4, InspectedPdf, PageInfo, has_complete_edition
from app.schemas import Claim, ClaimStatus, ClaimType
from app.service import summarize
from app.verification import deterministic_finding, undecided


def claim(kind, expected=None):
    return Claim(id="1", text="Exactly 2 pages", type=kind, source_quote="Exactly 2 pages", expected_value=expected)


def test_page_count_is_measured():
    pdf = InspectedPdf("planner.pdf", (PageInfo(1, "", 595.28, 841.89), PageInfo(2, "", 595.28, 841.89)), False)
    finding = deterministic_finding(claim(ClaimType.PAGE_COUNT, 2), [pdf])
    assert finding and finding.status == ClaimStatus.SUPPORTED
    assert has_complete_edition(pdf, A4)


def test_ambiguous_scope_is_unverified_and_summary_is_derived():
    finding = deterministic_finding(claim(ClaimType.PAGE_COUNT, 2), [])
    assert finding and finding.status == ClaimStatus.UNVERIFIED
    summary = summarize([finding, undecided(claim(ClaimType.SEMANTIC_CONTENT), "missing")])
    assert summary.unverified == 2


def test_pdf_file_format_is_deterministic():
    pdf = InspectedPdf("planner.pdf", (PageInfo(1, "", 1, 1),), False)
    finding = deterministic_finding(claim(ClaimType.FILE_FORMAT, "PDF"), [pdf])
    assert finding and finding.status == ClaimStatus.SUPPORTED


def test_worksheet_count_is_not_treated_as_pdf_page_count():
    pdf = InspectedPdf("planner.pdf", (PageInfo(1, "", 1, 1), PageInfo(2, "", 1, 1)), False)
    worksheet_claim = Claim(id="2", text="50 printable worksheets", type=ClaimType.PAGE_COUNT, source_quote="50 printable worksheets", expected_value=50)
    finding = deterministic_finding(worksheet_claim, [pdf])
    assert finding and finding.status == ClaimStatus.UNVERIFIED
