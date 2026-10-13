import asyncio

from app.documents import InspectedPdf, PageInfo
from app.retrieval import semantic_candidates
from app.schemas import Claim, ClaimType
from app.service import SemanticResults, semantic_findings


def test_retrieval_prefers_relevant_pages():
    claim = Claim(id="1", text="Savings goal tracker", type=ClaimType.SEMANTIC_CONTENT, source_quote="Savings")
    document = InspectedPdf("planner.pdf", (PageInfo(1, "notes", 1, 1), PageInfo(2, "Savings Goal Tracker", 1, 1)), False)
    assert semantic_candidates([claim], [document])[0] == ("planner.pdf", 2)


def test_incomplete_semantic_coverage_produces_warning():
    class Client:
        async def structured(self, *_):
            return SemanticResults()

    claim = Claim(id="1", text="Budget planner", type=ClaimType.SEMANTIC_CONTENT, source_quote="Budget")
    pages = tuple(PageInfo(number, "Budget planner", 1, 1) for number in range(1, 14))
    findings, warnings = asyncio.run(semantic_findings(Client(), [claim], [InspectedPdf("x.pdf", pages, False)]))
    assert findings[0].status.value == "UNVERIFIED"
    assert warnings == ["Semantic review examined 12 of 13 pages."]
