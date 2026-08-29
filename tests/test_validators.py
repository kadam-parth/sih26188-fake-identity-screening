"""Tests for stub modules — verify interfaces don't crash."""
from __future__ import annotations

import numpy as np
import pytest

from src.documents.detector import DocumentDetector
from src.documents.extractor import FieldExtractor
from src.documents.validators import DocumentValidator
from src.ocr.engine import OCREngine
from src.vision.tampering import TamperingAnalyzer
from src.verification.consistency import ConsistencyChecker
from src.risk.scoring import RiskScorer


class TestOCREngineStub:
    def test_init(self) -> None:
        engine = OCREngine()
        assert engine is not None

    def test_extract_returns_expected_keys(self) -> None:
        engine = OCREngine()
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        result = engine.extract_text(img)
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert "status" in result
        assert result["status"] == "not_implemented"


class TestDocumentDetectorStub:
    def test_init(self) -> None:
        detector = DocumentDetector()
        assert detector is not None

    def test_detect_returns_expected_keys(self) -> None:
        detector = DocumentDetector()
        result = detector.detect("sample text")
        assert isinstance(result, dict)
        assert "document_type" in result
        assert "document_name" in result
        assert "confidence" in result
        assert result["status"] == "not_implemented"


class TestFieldExtractorStub:
    def test_init(self) -> None:
        extractor = FieldExtractor()
        assert extractor is not None

    def test_extract_returns_expected_keys(self) -> None:
        extractor = FieldExtractor()
        result = extractor.extract("sample text", "aadhaar")
        assert isinstance(result, dict)
        assert "fields" in result
        assert "extraction_count" in result
        assert "total_fields" in result
        assert result["status"] == "not_implemented"

    def test_extract_unknown_doc_type(self) -> None:
        extractor = FieldExtractor()
        result = extractor.extract("text", "unknown_type")
        assert isinstance(result, dict)
        assert result["total_fields"] == 0


class TestDocumentValidatorStub:
    def test_init(self) -> None:
        validator = DocumentValidator()
        assert validator is not None

    def test_validate_returns_expected_keys(self) -> None:
        validator = DocumentValidator()
        result = validator.validate({}, "aadhaar")
        assert isinstance(result, dict)
        assert "checks" in result
        assert "valid_count" in result
        assert "total_count" in result
        assert "all_passed" in result


class TestTamperingAnalyzerStub:
    def test_init(self) -> None:
        analyzer = TamperingAnalyzer()
        assert analyzer is not None

    def test_analyze_returns_expected_keys(self) -> None:
        analyzer = TamperingAnalyzer()
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        result = analyzer.analyze(img)
        assert isinstance(result, dict)
        assert "checks" in result
        assert "ela_image" in result
        assert "overall_suspicious" in result
        assert "suspicion_score" in result


class TestConsistencyCheckerStub:
    def test_init(self) -> None:
        checker = ConsistencyChecker()
        assert checker is not None

    def test_single_doc_returns_insufficient(self) -> None:
        checker = ConsistencyChecker()
        result = checker.check([{"document_type": "aadhaar"}])
        assert result["status"] == "insufficient_documents"
        assert result["consistent"] is True

    def test_empty_list(self) -> None:
        checker = ConsistencyChecker()
        result = checker.check([])
        assert result["consistent"] is True


class TestRiskScorerStub:
    def test_init(self) -> None:
        scorer = RiskScorer()
        assert scorer is not None

    def test_calculate_returns_expected_keys(self) -> None:
        scorer = RiskScorer()
        result = scorer.calculate(
            validation_results={"checks": [], "valid_count": 0, "total_count": 0, "all_passed": True},
            tampering_results={"checks": [], "overall_suspicious": False, "suspicion_score": 0.0},
        )
        assert isinstance(result, dict)
        assert "score" in result
        assert "level" in result
        assert "recommendation" in result
        assert result["level"] in ("LOW", "MEDIUM", "HIGH")
