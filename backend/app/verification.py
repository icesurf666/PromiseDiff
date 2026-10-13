from __future__ import annotations

from .documents import A4, LETTER, InspectedPdf, has_complete_edition
from .schemas import Claim, ClaimStatus, FileMetadataEvidence, Finding, VerificationMethod


def deterministic_finding(claim: Claim, documents: list[InspectedPdf]) -> Finding | None:
    if claim.type == claim.type.COMPATIBILITY:
        return Finding(claim=claim, status=ClaimStatus.OUT_OF_SCOPE, method=VerificationMethod.NONE, reason="This app cannot test compatibility with another application.")
    if claim.type == claim.type.PAGE_COUNT:
        wording = f"{claim.text} {claim.scope or ''}".lower()
        if any(word in wording for word in ("worksheet", "worksheets", "template", "templates", "printable")):
            return undecided(claim, "A PDF page count cannot tell us how many worksheets or templates are included.")
        if len(documents) != 1 or not isinstance(claim.expected_value, int):
            return undecided(claim, "It is not clear which PDF or counting rule this claim refers to.")
        pdf = documents[0]
        return measured(claim, pdf.filename, "page_count", claim.expected_value, pdf.page_count)
    if claim.type == claim.type.FILE_PRESENCE and isinstance(claim.expected_value, str):
        found = any(pdf.filename.lower() == claim.expected_value.lower() for pdf in documents)
        return measured(claim, claim.expected_value, "file_presence", "present", "present" if found else "missing")
    if claim.type == claim.type.FILE_FORMAT:
        expected = str(claim.expected_value or "PDF").upper()
        observed = "PDF" if documents else "none"
        return measured(claim, ", ".join(pdf.filename for pdf in documents), "file_format", expected, observed)
    if claim.type == claim.type.PAGE_DIMENSIONS:
        asked = str(claim.expected_value or claim.text).lower()
        wants_a4, wants_letter = "a4" in asked, ("letter" in asked or "us letter" in asked)
        observed = []
        if wants_a4 and any(has_complete_edition(pdf, A4) for pdf in documents): observed.append("A4")
        if wants_letter and any(has_complete_edition(pdf, LETTER) for pdf in documents): observed.append("US Letter")
        expected = (["A4"] if wants_a4 else []) + (["US Letter"] if wants_letter else [])
        return measured(claim, ", ".join(pdf.filename for pdf in documents), "complete_editions", expected, observed)
    if claim.type == claim.type.EDITABILITY:
        forms = [pdf.filename for pdf in documents if pdf.has_forms]
        if forms:
            return Finding(claim=claim, status=ClaimStatus.SUPPORTED, method=VerificationMethod.DETERMINISTIC, reason="This PDF has fillable form fields.", evidence=[FileMetadataEvidence(filename=forms[0], property="acroform_fields", observed="present")])
        return undecided(claim, "We cannot confirm general editability from the delivered PDFs alone.")
    return None


def measured(claim: Claim, filename: str, prop: str, expected: object, observed: object) -> Finding:
    status = ClaimStatus.SUPPORTED if expected == observed else ClaimStatus.CONTRADICTED
    reason = f"Found {prop.replace('_', ' ')}: {observed!r}. The listing says: {expected!r}."
    return Finding(claim=claim, status=status, method=VerificationMethod.DETERMINISTIC, reason=reason, evidence=[FileMetadataEvidence(filename=filename, property=prop, expected=expected, observed=observed)])


def undecided(claim: Claim, reason: str) -> Finding:
    return Finding(claim=claim, status=ClaimStatus.UNVERIFIED, method=VerificationMethod.NONE, reason=reason)
