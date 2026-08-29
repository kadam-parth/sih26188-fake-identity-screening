from __future__ import annotations
import logging
import re
from typing import Optional
from src.config import DOCUMENT_TYPES

logger = logging.getLogger(__name__)


class FieldExtractor:
    """Extracts identity fields from OCR text using regex patterns.
    
    Currently a stub. Will be implemented on Day 4 using the regex patterns
    defined in DOCUMENT_TYPES config for each field.
    """
    
    def __init__(self):
        """Initialize with document type definitions from config."""
        self.document_types = DOCUMENT_TYPES
        logger.info("FieldExtractor initialized (stub)")
    
    def extract(self, ocr_text: str, document_type: str) -> dict:
        """Extract fields from OCR text for a given document type.
        
        Args:
            ocr_text: Raw text from OCR engine.
            document_type: Key from DOCUMENT_TYPES (e.g., 'aadhaar', 'pan').
            
        Returns:
            dict with keys:
                - fields (dict): Extracted field values keyed by field name.
                    Each value is a dict with 'value', 'confidence', 'label'.
                - raw_text (str): The original OCR text.
                - extraction_count (int): Number of fields successfully extracted.
                - total_fields (int): Number of fields defined for this doc type.
                - status (str): 'success', 'partial', 'no_fields', or 'not_implemented'
        """
        # TODO (Day 4): Implement regex-based field extraction
        
        doc_config = self.document_types.get(document_type, {})
        field_defs = doc_config.get("fields", {})
        
        logger.warning("Field extractor stub active — returning empty fields")
        return {
            "fields": {},
            "raw_text": ocr_text,
            "extraction_count": 0,
            "total_fields": len(field_defs),
            "status": "not_implemented",
            "message": "Field extractor not yet implemented.",
        }
