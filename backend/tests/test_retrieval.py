from app.documents import InspectedPdf, PageInfo
from app.retrieval import semantic_candidates
from app.schemas import Claim, ClaimType


def test_retrieval_prefers_relevant_pages():
    claim = Claim(id="1", text="Savings goal tracker", type=ClaimType.SEMANTIC_CONTENT, source_quote="Savings")
    document = InspectedPdf("planner.pdf", (PageInfo(1, "notes", 1, 1), PageInfo(2, "Savings Goal Tracker", 1, 1)), False)
    assert semantic_candidates([claim], [document])[0] == ("planner.pdf", 2)
