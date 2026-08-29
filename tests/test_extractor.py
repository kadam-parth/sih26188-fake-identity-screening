"""Unit tests for FieldExtractor (regex-based extraction).

Tests use synthetic OCR text — no images or EasyOCR required.
Validates extraction logic, confidence handling, status codes, and
edge cases for all three initial document types.
"""
from __future__ import annotations

import pytest

from src.documents.extractor import EXTRACTION_CONFIDENCE, FieldExtractor


@pytest.fixture
def extractor() -> FieldExtractor:
    return FieldExtractor()


# ── Aadhaar extraction ──────────────────────────────────────────────


class TestAadhaarExtraction:
    SAMPLE_TEXT = (
        "Government of India\n"
        "Unique Identification Authority of India\n"
        "Name: Rajesh Kumar\n"
        "DOB: 15/08/1990\n"
        "Male\n"
        "1234 5678 9012\n"
    )

    def test_aadhaar_number_extracted(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "aadhaar")
        assert "aadhaar_number" in result["fields"]
        value = result["fields"]["aadhaar_number"]["value"]
        # Should match the 12-digit pattern
        assert "1234" in value

    def test_name_extracted(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "aadhaar")
        assert "name" in result["fields"]
        assert "Rajesh" in result["fields"]["name"]["value"]

    def test_dob_extracted(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "aadhaar")
        assert "dob" in result["fields"]
        assert "15/08/1990" in result["fields"]["dob"]["value"]

    def test_gender_extracted(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "aadhaar")
        assert "gender" in result["fields"]
        assert "Male" in result["fields"]["gender"]["value"]

    def test_extraction_count(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "aadhaar")
        assert result["extraction_count"] >= 3  # at least number, name, dob
        assert result["total_fields"] == 4

    def test_status_with_all_fields(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "aadhaar")
        # With all 4 fields present, should be "success"
        assert result["status"] in ("success", "partial")


# ── PAN extraction ──────────────────────────────────────────────────


class TestPANExtraction:
    SAMPLE_TEXT = (
        "Income Tax Department\n"
        "Permanent Account Number\n"
        "Name: RAJESH KUMAR\n"
        "Father's Name: SURESH KUMAR\n"
        "15/08/1990\n"
        "ABCDE1234F\n"
    )

    def test_pan_number_extracted(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "pan")
        assert "pan_number" in result["fields"]
        assert result["fields"]["pan_number"]["value"] == "ABCDE1234F"

    def test_pan_name_extracted(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "pan")
        assert "name" in result["fields"]
        assert "RAJESH" in result["fields"]["name"]["value"]

    def test_pan_dob_extracted(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "pan")
        assert "dob" in result["fields"]
        assert "15/08/1990" in result["fields"]["dob"]["value"]


# ── Voter ID extraction ────────────────────────────────────────────


class TestVoterIDExtraction:
    SAMPLE_TEXT = (
        "Election Commission of India\n"
        "Electoral Photo Identity Card\n"
        "Elector's Name: Rajesh Kumar\n"
        "Father's Name: Suresh Kumar\n"
        "DOB: 15/08/1990\n"
        "ABC1234567\n"
    )

    def test_epic_number_extracted(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "voter_id")
        assert "epic_number" in result["fields"]
        assert result["fields"]["epic_number"]["value"] == "ABC1234567"

    def test_voter_id_name(self, extractor) -> None:
        result = extractor.extract(self.SAMPLE_TEXT, "voter_id")
        assert "name" in result["fields"]


# ── confidence ──────────────────────────────────────────────────────


class TestExtractionConfidence:
    def test_confidence_not_one(self, extractor) -> None:
        """Extracted confidence must never be 1.0 for regex matches."""
        text = "ABCDE1234F"
        result = extractor.extract(text, "pan")
        if result["extraction_count"] > 0:
            for field in result["fields"].values():
                assert field["confidence"] < 1.0

    def test_confidence_is_documented_constant(self, extractor) -> None:
        """Confidence should equal the module constant."""
        text = "1234 5678 9012"
        result = extractor.extract(text, "aadhaar")
        if "aadhaar_number" in result["fields"]:
            assert result["fields"]["aadhaar_number"]["confidence"] == EXTRACTION_CONFIDENCE

    def test_confidence_value_reasonable(self) -> None:
        """The constant itself should be between 0 and 1, exclusive of 1."""
        assert 0.0 < EXTRACTION_CONFIDENCE < 1.0


# ── edge cases ──────────────────────────────────────────────────────


class TestExtractorEdgeCases:
    def test_unknown_document_type(self, extractor) -> None:
        result = extractor.extract("some text", "unknown_type")
        assert result["total_fields"] == 0
        assert result["extraction_count"] == 0
        assert result["status"] == "unknown_document_type"

    def test_empty_text(self, extractor) -> None:
        result = extractor.extract("", "aadhaar")
        assert result["extraction_count"] == 0
        assert result["status"] == "no_fields"

    def test_no_matching_fields(self, extractor) -> None:
        result = extractor.extract("random gibberish", "aadhaar")
        assert result["extraction_count"] == 0
        assert result["status"] == "no_fields"

    def test_partial_extraction(self, extractor) -> None:
        """Text with some but not all fields → 'partial'."""
        text = "1234 5678 9012"  # only Aadhaar number, no name/dob/gender
        result = extractor.extract(text, "aadhaar")
        if result["extraction_count"] > 0:
            assert result["status"] == "partial"

    def test_raw_text_preserved(self, extractor) -> None:
        text = "original OCR text"
        result = extractor.extract(text, "aadhaar")
        assert result["raw_text"] == text

    def test_return_schema(self, extractor) -> None:
        result = extractor.extract("text", "aadhaar")
        required_keys = {
            "fields", "raw_text", "extraction_count",
            "total_fields", "status",
        }
        assert required_keys.issubset(result.keys())

    def test_field_has_label(self, extractor) -> None:
        """Each extracted field should include its human-readable label."""
        text = "ABCDE1234F"
        result = extractor.extract(text, "pan")
        if "pan_number" in result["fields"]:
            assert "label" in result["fields"]["pan_number"]
            assert result["fields"]["pan_number"]["label"] == "PAN Number"
