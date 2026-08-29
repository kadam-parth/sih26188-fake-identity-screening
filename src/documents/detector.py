from __future__ import annotations
import logging
from src.config import DOCUMENT_TYPES

logger = logging.getLogger(__name__)


class DocumentDetector:
    """Identifies document type from OCR-extracted text.
    
    Currently a stub. Will be implemented on Day 3 using keyword matching
    against DOCUMENT_TYPES definitions in config.
    """
    
    def __init__(self):
        """Initialize with document type definitions from config."""
        self.document_types = DOCUMENT_TYPES
        logger.info("DocumentDetector initialized (stub) — %d types registered",
                    len(self.document_types))
    
    def detect(self, ocr_text: str) -> dict:
        """Detect document type from OCR text.
        
        Args:
            ocr_text: Raw text string from OCR engine.
            
        Returns:
            dict with keys:
                - document_type (str | None): Key from DOCUMENT_TYPES or None
                - document_name (str): Human-readable name
                - confidence (float): Detection confidence (0.0–1.0)
                - matched_keywords (list[str]): Keywords that matched
                - status (str): 'success', 'no_match', or 'not_implemented'
        """
        # TODO (Day 3): Implement keyword frequency matching
        # For each doc type, count keyword hits in ocr_text.
        # The type with the most hits (above a threshold) wins.
        
        logger.warning("Document detector stub active — returning no match")
        return {
            "document_type": None,
            "document_name": "Unknown",
            "confidence": 0.0,
            "matched_keywords": [],
            "status": "not_implemented",
            "message": "Document detector not yet implemented.",
        }
