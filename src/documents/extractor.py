"""Regex-based identity-field extraction from OCR text.

Applies the regex patterns defined in ``src.config.DOCUMENT_TYPES`` to
extract structured fields (names, ID numbers, dates, etc.) from raw
OCR output.

Extraction confidence
---------------------
A successful regex match does **not** prove the extracted value is
correct — OCR text may contain errors and the regex may capture a
false positive.  Therefore, extracted fields are assigned a heuristic
confidence of ``EXTRACTION_CONFIDENCE`` (default 0.7) rather than
1.0.  This value is **not** a calibrated probability.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from src.config import DOCUMENT_TYPES

logger = logging.getLogger(__name__)

# Heuristic confidence assigned to every regex extraction.
# Rationale: a regex match confirms the *pattern* was found in OCR text,
# but OCR noise, misreads, and regex over-matching mean the extracted
# value may still be incorrect.  0.7 signals "likely but not certain".
# This is NOT a calibrated probability.
EXTRACTION_CONFIDENCE: float = 0.7


class FieldExtractor:
    """Extracts identity fields from OCR text using regex patterns.

    For each field defined in the matching ``DOCUMENT_TYPES`` entry the
    extractor compiles the associated regex, searches the OCR text, and
    returns the first match (capturing-group 1 when present, otherwise
    group 0).
    """

    def __init__(self) -> None:
        """Initialize with document type definitions from config."""
        self.document_types = DOCUMENT_TYPES
        logger.info("FieldExtractor initialized")

    # ── public API ───────────────────────────────────────────────────

    def extract(self, ocr_text: str, document_type: str) -> dict:
        """Extract fields from *ocr_text* for a given *document_type*.

        Args:
            ocr_text: Raw text from the OCR engine.
            document_type: Key from ``DOCUMENT_TYPES`` (e.g. ``'aadhaar'``).

        Returns:
            dict with keys:
                - **fields** (*dict*): Mapping of field-name →
                  ``{value, confidence, label}``.
                - **raw_text** (*str*): The original OCR text.
                - **extraction_count** (*int*): Fields successfully
                  extracted.
                - **total_fields** (*int*): Fields defined for this
                  document type.
                - **status** (*str*): ``"success"`` | ``"partial"``
                  | ``"no_fields"`` | ``"unknown_document_type"``.
        """
        doc_config = self.document_types.get(document_type)

        # ── unknown document type ────────────────────────────────────
        if doc_config is None:
            logger.warning(
                "Unknown document type '%s' — no fields to extract",
                document_type,
            )
            return {
                "fields": {},
                "raw_text": ocr_text,
                "extraction_count": 0,
                "total_fields": 0,
                "status": "unknown_document_type",
                "message": f"Unknown document type: {document_type}",
            }

        field_defs: dict[str, dict[str, Any]] = doc_config.get("fields", {})
        total = len(field_defs)

        if not ocr_text or not ocr_text.strip():
            logger.info("Empty OCR text — nothing to extract")
            return {
                "fields": {},
                "raw_text": ocr_text or "",
                "extraction_count": 0,
                "total_fields": total,
                "status": "no_fields",
                "message": "Empty OCR text provided.",
            }

        # ── run extraction ───────────────────────────────────────────
        fields: dict[str, dict] = {}

        for field_name, field_cfg in field_defs.items():
            pattern = field_cfg.get("pattern")
            if not pattern:
                continue

            value = self._extract_field(pattern, ocr_text)
            if value is not None:
                fields[field_name] = {
                    "value": value,
                    "confidence": EXTRACTION_CONFIDENCE,
                    "label": field_cfg.get("label", field_name),
                }

        count = len(fields)
        status = self._determine_status(count, total)

        logger.info(
            "Extraction for '%s': %d / %d fields (%s)",
            document_type,
            count,
            total,
            status,
        )

        return {
            "fields": fields,
            "raw_text": ocr_text,
            "extraction_count": count,
            "total_fields": total,
            "status": status,
        }

    # ── internal helpers ─────────────────────────────────────────────

    @staticmethod
    def _extract_field(pattern: str, text: str) -> str | None:
        """Return the first match of *pattern* in *text*, or ``None``.

        If the regex contains a capturing group, group(1) is returned;
        otherwise group(0) (the full match) is used.  Leading/trailing
        whitespace is stripped.
        """
        try:
            match = re.search(pattern, text, re.IGNORECASE)
        except re.error as exc:
            logger.warning("Invalid regex pattern '%s': %s", pattern, exc)
            return None

        if match is None:
            return None

        # Prefer first capturing group when available
        if match.lastindex and match.lastindex >= 1:
            value = match.group(1)
        else:
            value = match.group(0)

        return value.strip() if value else None

    @staticmethod
    def _determine_status(extracted: int, total: int) -> str:
        """Classify extraction outcome."""
        if total == 0:
            return "no_fields"
        if extracted == 0:
            return "no_fields"
        if extracted >= total:
            return "success"
        return "partial"
