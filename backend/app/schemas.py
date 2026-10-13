from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class ClaimType(str, Enum):
    PAGE_COUNT = "PAGE_COUNT"
    FILE_PRESENCE = "FILE_PRESENCE"
    FILE_FORMAT = "FILE_FORMAT"
    PAGE_DIMENSIONS = "PAGE_DIMENSIONS"
    SEMANTIC_CONTENT = "SEMANTIC_CONTENT"
    EDITABILITY = "EDITABILITY"
    COMPATIBILITY = "COMPATIBILITY"


class ClaimStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNVERIFIED = "UNVERIFIED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class VerificationMethod(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    SEMANTIC = "SEMANTIC"
    NONE = "NONE"


class Claim(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: str
    text: str
    type: ClaimType
    source_quote: str
    expected_value: int | str | list[str] | None = None
    scope: str | None = None


class DocumentTextEvidence(BaseModel):
    kind: Literal["DOCUMENT_TEXT"] = "DOCUMENT_TEXT"
    filename: str
    page: int = Field(ge=1)
    quote: str


class FileMetadataEvidence(BaseModel):
    kind: Literal["FILE_METADATA"] = "FILE_METADATA"
    filename: str
    property: str
    expected: int | str | list[str] | None = None
    observed: int | str | list[str]


Evidence = Annotated[DocumentTextEvidence | FileMetadataEvidence, Field(discriminator="kind")]


class Finding(BaseModel):
    claim: Claim
    status: ClaimStatus
    method: VerificationMethod
    reason: str
    evidence: list[Evidence] = []


class Summary(BaseModel):
    supported: int = 0
    contradicted: int = 0
    unverified: int = 0
    out_of_scope: int = 0


class AnalysisResponse(BaseModel):
    summary: Summary
    findings: list[Finding]
    warnings: list[str] = []


class ErrorResponse(BaseModel):
    detail: str
