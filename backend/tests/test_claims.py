from app.claims import content_fallback, validate_claims
from app.schemas import Claim, ClaimType


def test_a4_and_letter_claim_is_normalized_to_dimensions():
    quote = "Includes both A4 and US Letter PDF editions."
    claim = Claim(id="1", text=quote, type=ClaimType.FILE_FORMAT, source_quote=quote)
    accepted = validate_claims(quote, [claim])
    assert accepted[0].type == ClaimType.PAGE_DIMENSIONS
    assert accepted[0].expected_value == ["A4", "US Letter"]


def test_invented_listing_quote_is_discarded():
    claim = Claim(id="1", text="x", type=ClaimType.SEMANTIC_CONTENT, source_quote="invented")
    assert validate_claims("actual listing", [claim]) == []


def test_explicit_content_item_is_not_silently_lost():
    result = content_fallback("Includes savings goal trackers.", [])
    assert result[0].type == ClaimType.SEMANTIC_CONTENT


def test_fallback_does_not_duplicate_model_quote_with_punctuation_change():
    text = "Contains savings goal trackers."
    claim = Claim(id="1", text=text, type=ClaimType.SEMANTIC_CONTENT, source_quote=text[:-1])
    assert content_fallback(text, [claim]) == [claim]
